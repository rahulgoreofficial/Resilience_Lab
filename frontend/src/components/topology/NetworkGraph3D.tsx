import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import type { 
  NetworkTopologyResponse, 
  CytoscapeNodeData, 
  CytoscapeEdgeData 
} from '../../types/network';
import { RotateCw, Maximize2, Layers, Globe, Compass } from 'lucide-react';

export interface NetworkGraph3DProps {
  topology: NetworkTopologyResponse | null;
  selectedNodeId?: string | null;
  selectedEdgeId?: string | null;
  onSelectNode?: (nodeData: CytoscapeNodeData | null) => void;
  onSelectEdge?: (edgeData: CytoscapeEdgeData | null) => void;
  highlightedPath?: string[];
  failedNodeIds?: string[];
  failedEdgeIds?: string[];
  articulationPoints?: string[];
  bridgeEdgeIds?: string[];
  className?: string;
}

type Layout3DType = 'layered' | 'sphere' | 'spiral';

interface NodeMeshUserData {
  nodeData: CytoscapeNodeData;
  isFailed: boolean;
  isAP: boolean;
  inPath: boolean;
  pulseMesh?: THREE.Mesh;
}

export const NetworkGraph3D: React.FC<NetworkGraph3DProps> = ({
  topology,
  selectedNodeId,
  onSelectNode,
  highlightedPath = [],
  failedNodeIds = [],
  failedEdgeIds = [],
  articulationPoints = [],
  bridgeEdgeIds = [],
  className = ''
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<{ data: CytoscapeNodeData; x: number; y: number } | null>(null);
  const [autoRotate, setAutoRotate] = useState(false);
  const [layoutMode, setLayoutMode] = useState<Layout3DType>('layered');
  const [controlsRef, setControlsRef] = useState<OrbitControls | null>(null);
  const [cameraRef, setCameraRef] = useState<THREE.PerspectiveCamera | null>(null);

  // Compute 3D node positions based on layout
  const computePositions = useCallback((nodes: CytoscapeNodeData[], mode: Layout3DType) => {
    const posMap = new Map<string, THREE.Vector3>();
    const count = nodes.length;
    if (count === 0) return posMap;

    if (mode === 'sphere') {
      const radius = Math.max(120, count * 15);
      const phi = Math.PI * (3 - Math.sqrt(5)); // Golden angle
      nodes.forEach((node, i) => {
        const y = 1 - (i / (count - 1 || 1)) * 2;
        const radiusAtY = Math.sqrt(1 - y * y);
        const theta = phi * i;
        const x = Math.cos(theta) * radiusAtY;
        const z = Math.sin(theta) * radiusAtY;
        posMap.set(node.id, new THREE.Vector3(x * radius, y * radius, z * radius));
      });
    } else if (mode === 'spiral') {
      const spacing = 18;
      nodes.forEach((node, i) => {
        const theta = i * 0.45;
        const r = 30 + i * spacing * 0.35;
        const x = Math.cos(theta) * r;
        const z = Math.sin(theta) * r;
        const y = (i - count / 2) * 8;
        posMap.set(node.id, new THREE.Vector3(x, y, z));
      });
    } else {
      // Layered Hierarchical 3D Layout
      // Tier 1 (Top): Gateways
      // Tier 2: Firewalls
      // Tier 3 (Middle): Routers
      // Tier 4: Switches
      // Tier 5 (Base): Servers & Databases
      const tiers: Record<string, CytoscapeNodeData[]> = {
        gateway: [],
        firewall: [],
        router: [],
        switch: [],
        server: [],
        database: []
      };

      nodes.forEach(n => {
        const t = n.node_type.toLowerCase();
        if (tiers[t]) {
          tiers[t].push(n);
        } else {
          tiers.router.push(n);
        }
      });

      const tierY: Record<string, number> = {
        gateway: 110,
        firewall: 65,
        router: 10,
        switch: -45,
        server: -100,
        database: -140
      };

      Object.entries(tiers).forEach(([type, tierNodes]) => {
        const y = tierY[type] ?? 0;
        const tCount = tierNodes.length;
        const radius = Math.max(45, tCount * 22);

        tierNodes.forEach((node, i) => {
          const angle = (i / (tCount || 1)) * Math.PI * 2;
          const x = Math.cos(angle) * radius;
          const z = Math.sin(angle) * radius;
          posMap.set(node.id, new THREE.Vector3(x, y, z));
        });
      });
    }

    return posMap;
  }, []);

  useEffect(() => {
    const container = mountRef.current;
    if (!container || !topology) return;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0f1d);
    scene.fog = new THREE.FogExp2(0x0a0f1d, 0.0018);

    const width = container.clientWidth;
    const height = container.clientHeight;

    const camera = new THREE.PerspectiveCamera(50, width / height, 1, 3000);
    camera.position.set(0, 160, 360);
    setCameraRef(camera);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.replaceChildren(renderer.domElement);

    // 2. Orbit Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 1200;
    controls.minDistance = 60;
    controls.autoRotate = autoRotate;
    controls.autoRotateSpeed = 1.2;
    setControlsRef(controls);

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight1.position.set(150, 250, 150);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x0070f3, 0.8);
    dirLight2.position.set(-150, -100, -150);
    scene.add(dirLight2);

    // Cybernetic coordinate grid floor
    const gridHelper = new THREE.GridHelper(600, 30, 0x1e293b, 0x0f172a);
    gridHelper.position.y = -160;
    scene.add(gridHelper);

    // 4. Geometry and Material Palette
    const nodeMeshes: THREE.Mesh[] = [];
    const pulseObjects: { mesh: THREE.Mesh; baseScale: number }[] = [];
    const flowParticles: { curve: THREE.LineCurve3; t: number; speed: number; mesh: THREE.Mesh }[] = [];

    const nodesData = topology.elements.nodes.map(n => n.data);
    const edgesData = topology.elements.edges.map(e => e.data);
    const positions = computePositions(nodesData, layoutMode);

    // Particle geometry for data pulses
    const particleGeo = new THREE.SphereGeometry(1.2, 8, 8);
    const particleMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });

    // Build Nodes
    nodesData.forEach(node => {
      const pos = positions.get(node.id) || new THREE.Vector3();
      const isFailed = failedNodeIds.includes(node.id);
      const isAP = articulationPoints.includes(node.id);
      const inPath = highlightedPath.includes(node.id);
      const isSelected = selectedNodeId === node.id;

      let geom: THREE.BufferGeometry;
      let baseColor: number;

      // Type-specific 3D geometries
      switch (node.node_type.toLowerCase()) {
        case 'gateway':
          geom = new THREE.IcosahedronGeometry(9, 1);
          baseColor = 0xa855f7; // Purple
          break;
        case 'firewall':
          geom = new THREE.BoxGeometry(11, 11, 11);
          baseColor = 0xf97316; // Orange
          break;
        case 'router':
          geom = new THREE.OctahedronGeometry(9, 1);
          baseColor = 0x06b6d4; // Cyan
          break;
        case 'switch':
          geom = new THREE.DodecahedronGeometry(8);
          baseColor = 0x10b981; // Emerald
          break;
        case 'database':
          geom = new THREE.CylinderGeometry(8, 8, 12, 16);
          baseColor = 0xf59e0b; // Amber
          break;
        case 'server':
        default:
          geom = new THREE.CylinderGeometry(7, 7, 10, 12);
          baseColor = 0x3b82f6; // Blue
          break;
      }

      let mat: THREE.Material;
      if (isFailed) {
        mat = new THREE.MeshStandardMaterial({
          color: 0xef4444,
          roughness: 0.7,
          metalness: 0.2,
          emissive: 0x7f1d1d,
          emissiveIntensity: 0.6,
          wireframe: true
        });
      } else if (inPath) {
        mat = new THREE.MeshStandardMaterial({
          color: 0x38bdf8,
          emissive: 0x0284c7,
          emissiveIntensity: 0.8,
          roughness: 0.2,
          metalness: 0.8
        });
      } else {
        mat = new THREE.MeshStandardMaterial({
          color: baseColor,
          roughness: 0.3,
          metalness: 0.4,
          emissive: baseColor,
          emissiveIntensity: 0.25
        });
      }

      const mesh = new THREE.Mesh(geom, mat);
      mesh.position.copy(pos);
      mesh.castShadow = true;
      mesh.receiveShadow = true;

      const userData: NodeMeshUserData = {
        nodeData: node,
        isFailed,
        isAP,
        inPath
      };

      // Articulation Point glowing pulse halo
      if (isAP && !isFailed) {
        const ringGeo = new THREE.TorusGeometry(14, 1.2, 8, 24);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, wireframe: true, transparent: true, opacity: 0.85 });
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.position.copy(pos);
        ringMesh.rotation.x = Math.PI / 2;
        scene.add(ringMesh);
        userData.pulseMesh = ringMesh;
        pulseObjects.push({ mesh: ringMesh, baseScale: 1.0 });
      }

      // Selection Halo
      if (isSelected) {
        const selGeo = new THREE.SphereGeometry(15, 16, 16);
        const selMat = new THREE.MeshBasicMaterial({ color: 0x60a5fa, wireframe: true, transparent: true, opacity: 0.5 });
        const selMesh = new THREE.Mesh(selGeo, selMat);
        selMesh.position.copy(pos);
        scene.add(selMesh);
      }

      mesh.userData = userData;
      scene.add(mesh);
      nodeMeshes.push(mesh);
    });

    // Build Edges
    edgesData.forEach((edge, i) => {
      const srcPos = positions.get(edge.source);
      const tgtPos = positions.get(edge.target);
      if (!srcPos || !tgtPos) return;

      const isFailed = failedEdgeIds.includes(edge.id) || failedNodeIds.includes(edge.source) || failedNodeIds.includes(edge.target);
      const isBridge = bridgeEdgeIds.includes(edge.id);
      const inPath = highlightedPath.includes(edge.source) && highlightedPath.includes(edge.target);

      let lineColor = 0x334155;
      let lineWidth = 1;
      let opacity = 0.4;

      if (isFailed) {
        lineColor = 0xef4444;
        opacity = 0.25;
      } else if (inPath) {
        lineColor = 0x06b6d4;
        lineWidth = 3;
        opacity = 0.95;
      } else if (isBridge) {
        lineColor = 0xf59e0b;
        lineWidth = 2;
        opacity = 0.85;
      }

      const points = [srcPos, tgtPos];
      const lineGeom = new THREE.BufferGeometry().setFromPoints(points);
      const lineMat = new THREE.LineBasicMaterial({
        color: lineColor,
        linewidth: lineWidth,
        transparent: true,
        opacity: opacity
      });

      const line = new THREE.Line(lineGeom, lineMat);
      scene.add(line);

      // Add active flowing traffic packet along operational links
      if (!isFailed && i % 2 === 0) {
        const pMesh = new THREE.Mesh(particleGeo, particleMat);
        scene.add(pMesh);
        flowParticles.push({
          curve: new THREE.LineCurve3(srcPos, tgtPos),
          t: (i * 0.15) % 1.0,
          speed: 0.003 + (i % 3) * 0.001,
          mesh: pMesh
        });
      }
    });

    // 5. Raycasting for Interaction
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const handleMouseMove = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      if (intersects.length > 0) {
        const hit = intersects[0].object as THREE.Mesh;
        const uData = hit.userData as NodeMeshUserData;
        container.style.cursor = 'pointer';
        setHoveredNode({
          data: uData.nodeData,
          x: event.clientX - rect.left,
          y: event.clientY - rect.top
        });
      } else {
        container.style.cursor = 'default';
        setHoveredNode(null);
      }
    };

    const handleClick = (event: MouseEvent) => {
      const rect = container.getBoundingClientRect();
      mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodeMeshes);

      if (intersects.length > 0) {
        const hit = intersects[0].object as THREE.Mesh;
        const uData = hit.userData as NodeMeshUserData;
        if (onSelectNode) {
          onSelectNode(uData.nodeData);
        }
      } else {
        if (onSelectNode) {
          onSelectNode(null);
        }
      }
    };

    container.addEventListener('mousemove', handleMouseMove);
    container.addEventListener('click', handleClick);

    // 6. Resize Handler
    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(container);

    // 7. Animation Loop
    let animId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      animId = requestAnimationFrame(animate);
      clock.getDelta();
      const elapsed = clock.getElapsedTime();

      controls.update();

      // Pulse articulation point rings
      pulseObjects.forEach(p => {
        const s = 1.0 + Math.sin(elapsed * 4.0) * 0.18;
        p.mesh.scale.set(s, s, s);
        p.mesh.rotation.z += 0.015;
      });

      // Flow active traffic packets along edges
      flowParticles.forEach(fp => {
        fp.t = (fp.t + fp.speed) % 1.0;
        fp.curve.getPoint(fp.t, fp.mesh.position);
      });

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      cancelAnimationFrame(animId);
      container.removeEventListener('mousemove', handleMouseMove);
      container.removeEventListener('click', handleClick);
      resizeObserver.disconnect();
      controls.dispose();
      renderer.dispose();
    };
  }, [topology, layoutMode, computePositions, autoRotate, failedNodeIds, failedEdgeIds, articulationPoints, bridgeEdgeIds, highlightedPath, selectedNodeId, onSelectNode]);

  // Viewport action handlers
  const handleResetCamera = () => {
    if (!controlsRef || !cameraRef) return;
    cameraRef.position.set(0, 160, 360);
    controlsRef.target.set(0, 0, 0);
    controlsRef.update();
  };

  const toggleAutoRotate = () => {
    setAutoRotate(prev => {
      if (controlsRef) controlsRef.autoRotate = !prev;
      return !prev;
    });
  };

  return (
    <div className={`relative w-full h-full min-h-[500px] overflow-hidden bg-[#0A0F1D] rounded-xl border border-[#1E293B] shadow-inner ${className}`}>
      {/* Three.js Canvas Container */}
      <div ref={mountRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Floating 3D Interaction HUD Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 bg-[#0B1120]/90 backdrop-blur-md px-2.5 py-1.5 rounded-lg border border-[#1E293B] shadow-lg text-xs">
        <button
          onClick={handleResetCamera}
          title="Reset 3D Camera"
          className="p-1.5 text-gray-400 hover:text-white hover:bg-[#1E293B] rounded transition-colors"
        >
          <Maximize2 className="w-4 h-4" />
        </button>

        <button
          onClick={toggleAutoRotate}
          title={autoRotate ? "Pause Orbit" : "Auto-Rotate Scene"}
          className={`p-1.5 rounded transition-colors ${autoRotate ? 'text-[#0070F3] bg-[#0070F3]/15' : 'text-gray-400 hover:text-white hover:bg-[#1E293B]'}`}
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <div className="w-[1px] h-4 bg-[#1E293B] mx-1" />

        {/* 3D Layout Selector */}
        <div className="flex items-center gap-1">
          <button
            onClick={() => setLayoutMode('layered')}
            className={`px-2 py-1 rounded font-mono text-[11px] flex items-center gap-1 transition-colors ${layoutMode === 'layered' ? 'bg-[#0070F3] text-white' : 'text-gray-400 hover:text-white'}`}
            title="Layered Tier Layout"
          >
            <Layers className="w-3 h-3" /> Tiers
          </button>
          <button
            onClick={() => setLayoutMode('sphere')}
            className={`px-2 py-1 rounded font-mono text-[11px] flex items-center gap-1 transition-colors ${layoutMode === 'sphere' ? 'bg-[#0070F3] text-white' : 'text-gray-400 hover:text-white'}`}
            title="Spherical 3D Globe Layout"
          >
            <Globe className="w-3 h-3" /> Globe
          </button>
          <button
            onClick={() => setLayoutMode('spiral')}
            className={`px-2 py-1 rounded font-mono text-[11px] flex items-center gap-1 transition-colors ${layoutMode === 'spiral' ? 'bg-[#0070F3] text-white' : 'text-gray-400 hover:text-white'}`}
            title="3D Helical Spiral"
          >
            <Compass className="w-3 h-3" /> Spiral
          </button>
        </div>
      </div>

      {/* 3D Floating Node Hover HUD */}
      {hoveredNode && (
        <div
          className="absolute z-30 pointer-events-none bg-[#0B1120]/95 backdrop-blur-md border border-[#334155] rounded-lg p-3 text-white shadow-2xl text-[11px] font-sans transition-all duration-75"
          style={{
            left: Math.min(hoveredNode.x + 15, (mountRef.current?.clientWidth || 800) - 220),
            top: Math.max(hoveredNode.y - 40, 10),
            minWidth: '200px'
          }}
        >
          <div className="flex items-center justify-between pb-1.5 border-b border-[#1E293B] mb-2">
            <span className="font-bold text-sm text-[#38BDF8] font-mono">{hoveredNode.data.id}</span>
            <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-[#1E293B] text-gray-300">
              {hoveredNode.data.node_type}
            </span>
          </div>
          <div className="space-y-1 text-gray-300">
            <div className="flex justify-between">
              <span className="text-gray-400">Capacity:</span>
              <span className="font-mono text-white">{hoveredNode.data.capacity} Mbps</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Current Load:</span>
              <span className="font-mono text-white">{hoveredNode.data.current_load} Mbps</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Importance:</span>
              <span className="font-mono text-white">{hoveredNode.data.importance}</span>
            </div>
            {failedNodeIds.includes(hoveredNode.data.id) && (
              <div className="pt-1 text-red-400 font-semibold flex items-center gap-1">
                ● STATUS: FAILED / OFFLINE
              </div>
            )}
            {articulationPoints.includes(hoveredNode.data.id) && (
              <div className="pt-1 text-amber-400 font-semibold flex items-center gap-1">
                ▲ CRITICAL ARTICULATION POINT
              </div>
            )}
          </div>
        </div>
      )}

      {/* Bottom HUD Legend */}
      <div className="absolute bottom-3 left-3 z-20 flex items-center gap-4 bg-[#0B1120]/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#1E293B] text-[10px] text-gray-400">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#06B6D4]" />
          <span>Router</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]" />
          <span>Switch</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#3B82F6]" />
          <span>Server</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]" />
          <span>Database</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-[#A855F7]" />
          <span>Gateway</span>
        </div>
        <div className="flex items-center gap-1.5 pl-2 border-l border-[#1E293B]">
          <span className="w-2.5 h-2.5 rounded-full border border-amber-400 bg-amber-400/30 animate-pulse" />
          <span className="text-amber-300">Cut-Vertex (AP)</span>
        </div>
      </div>
    </div>
  );
};
