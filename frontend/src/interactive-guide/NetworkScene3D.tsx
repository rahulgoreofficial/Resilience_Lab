/**
 * NetworkScene3D - Core Three.js / React Three Fiber visualization for the guide.
 * Pure 3D scene: nodes, edges, labels. No UI overlays.
 */

import React, { useRef, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import * as THREE from 'three';

import type { CytoscapeNodeData, CytoscapeEdgeData } from '../types/network';
import type { NodeState, EdgeState } from './guideTypes';

// ─── Colour palette (consistent with app design) ─────────────────────────────
const COLORS = {
  gateway:    '#7C3AED',  // violet
  firewall:   '#DC2626',  // red-600
  router:     '#2563EB',  // blue-600
  switch:     '#0891B2',  // cyan-600
  server:     '#059669',  // emerald-600
  database:   '#D97706',  // amber-600
  healthy:    '#22C55E',
  critical:   '#F59E0B',
  failed:     '#EF4444',
  disconnected: '#64748B',
  selected:   '#22D3EE',
  highlighted:'#F59E0B',
  edge:       '#334155',
  bridge:     '#F59E0B',
  activePath: '#22D3EE',
};

type NodeColor = keyof typeof COLORS;

function nodeBaseColor(type: string): string {
  return COLORS[type as NodeColor] ?? COLORS.server;
}

function statusColor(status: NodeState['status'], type: string): string {
  switch (status) {
    case 'failed':       return COLORS.failed;
    case 'critical':     return COLORS.critical;
    case 'disconnected': return COLORS.disconnected;
    case 'selected':     return COLORS.selected;
    case 'highlighted':  return COLORS.highlighted;
    default:             return nodeBaseColor(type);
  }
}

// ─── Stable 3D Layout Engine ─────────────────────────────────────────────────
function computeLayout(
  nodes: CytoscapeNodeData[],
  edges: CytoscapeEdgeData[]
): Map<string, THREE.Vector3> {
  const positions = new Map<string, THREE.Vector3>();
  if (nodes.length === 0) return positions;

  // Tier-based layered layout
  const tierOrder: Record<string, number> = {
    gateway: 0, firewall: 1, router: 2, switch: 3, server: 4, database: 4,
  };
  const tiers = new Map<number, string[]>();

  for (const n of nodes) {
    const tier = tierOrder[n.node_type] ?? 3;
    if (!tiers.has(tier)) tiers.set(tier, []);
    tiers.get(tier)!.push(n.id);
  }

  const sortedTiers = Array.from(tiers.entries()).sort((a, b) => a[0] - b[0]);
  const totalTiers = sortedTiers.length;
  const ySpread = 3.5;
  const xSpread = 3.5;

  sortedTiers.forEach(([, ids], tierIdx) => {
    const y = ((totalTiers - 1) / 2 - tierIdx) * ySpread;
    ids.forEach((id, idx) => {
      const x = (idx - (ids.length - 1) / 2) * xSpread;
      // deterministic slight z offset by id hash
      const z = ((id.charCodeAt(0) * 7 + id.charCodeAt(id.length - 1) * 3) % 100) / 50 - 1;
      positions.set(id, new THREE.Vector3(x, y, z));
    });
  });

  void edges; // layout doesn't use edges currently but param kept for future spring layout
  return positions;
}

// ─── Individual Node Component ─────────────────────────────────────────────
interface NetworkNode3DProps {
  node: CytoscapeNodeData;
  position: THREE.Vector3;
  nodeState?: NodeState;
  onSelect: (id: string) => void;
  onHover: (id: string | null) => void;
  isHovered: boolean;
}

function NetworkNode3D({ node, position, nodeState, onSelect, onHover, isHovered }: NetworkNode3DProps) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const ringRef = useRef<THREE.Mesh>(null!);
  const status = nodeState?.status ?? 'healthy';
  const color = statusColor(status, node.node_type);
  const isAP = nodeState?.isArticulationPoint;
  const isBridge = nodeState?.isBridge;

  useFrame((_, delta) => {
    if (meshRef.current) {
      // Pulse scale for critical/selected nodes
      if (status === 'critical' || status === 'selected') {
        meshRef.current.scale.setScalar(1 + Math.sin(Date.now() * 0.004) * 0.08);
      } else if (isHovered) {
        meshRef.current.scale.lerp(new THREE.Vector3(1.2, 1.2, 1.2), 0.15);
      } else {
        meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.15);
      }
    }
    if (ringRef.current && isAP) {
      ringRef.current.rotation.z += delta * 1.2;
    }
  });

  // Choose geometry based on node type
  const geometry = useMemo(() => {
    switch (node.node_type) {
      case 'gateway':  return <icosahedronGeometry args={[0.52, 0]} />;
      case 'firewall': return <boxGeometry args={[0.85, 0.85, 0.85]} />;
      case 'router':   return <octahedronGeometry args={[0.55, 0]} />;
      case 'switch':   return <dodecahedronGeometry args={[0.48, 0]} />;
      case 'server':   return <cylinderGeometry args={[0.35, 0.35, 0.8, 8]} />;
      case 'database': return <cylinderGeometry args={[0.42, 0.42, 0.5, 12]} />;
      default:         return <sphereGeometry args={[0.4, 12, 12]} />;
    }
  }, [node.node_type]);

  const emissiveIntensity = status === 'failed' ? 0.4 : status === 'selected' ? 0.3 : isHovered ? 0.2 : 0.05;

  return (
    <group position={position}>
      {/* Main node mesh */}
      <mesh
        ref={meshRef}
        onClick={(e) => { e.stopPropagation(); onSelect(node.id); }}
        onPointerOver={(e) => { e.stopPropagation(); onHover(node.id); }}
        onPointerOut={() => onHover(null)}
        castShadow
      >
        {geometry}
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          metalness={0.3}
          roughness={0.5}
        />
      </mesh>

      {/* Articulation point ring */}
      {isAP && (
        <mesh ref={ringRef}>
          <torusGeometry args={[0.78, 0.04, 6, 24]} />
          <meshStandardMaterial color={COLORS.critical} emissive={COLORS.critical} emissiveIntensity={0.6} />
        </mesh>
      )}

      {/* Failure overlay wireframe */}
      {status === 'failed' && (
        <mesh>
          <sphereGeometry args={[0.72, 8, 8]} />
          <meshBasicMaterial color={COLORS.failed} wireframe opacity={0.4} transparent />
        </mesh>
      )}

      {/* Label */}
      <Text
        position={[0, 0.95, 0]}
        fontSize={0.22}
        color={isHovered ? '#FFFFFF' : '#CBD5E1'}
        anchorX="center"
        anchorY="bottom"
        outlineColor="#0B1120"
        outlineWidth={0.02}
        renderOrder={10}
      >
        {node.label?.substring(0, 18) ?? node.id}
      </Text>

      {/* Type badge */}
      <Text
        position={[0, -0.85, 0]}
        fontSize={0.16}
        color={color}
        anchorX="center"
        anchorY="top"
        renderOrder={10}
      >
        {node.node_type.toUpperCase()}
      </Text>

      {isBridge && (
        <Text
          position={[0.65, 0.3, 0]}
          fontSize={0.14}
          color={COLORS.bridge}
          anchorX="left"
          renderOrder={10}
        >
          ⚠ BRIDGE
        </Text>
      )}
    </group>
  );
}

// ─── Edge Component ─────────────────────────────────────────────────────────
interface NetworkEdge3DProps {
  edge: CytoscapeEdgeData;
  sourcePos: THREE.Vector3;
  targetPos: THREE.Vector3;
  edgeState?: EdgeState;
  onSelect: (id: string) => void;
}

function NetworkEdge3D({ edge, sourcePos, targetPos, edgeState, onSelect }: NetworkEdge3DProps) {
  const status = edgeState?.status ?? 'healthy';

  const color = useMemo(() => {
    if (status === 'failed')      return COLORS.failed;
    if (status === 'bridge')      return COLORS.bridge;
    if (status === 'active_path') return COLORS.activePath;
    return COLORS.edge;
  }, [status]);

  const points = useMemo(
    () => [sourcePos.clone(), targetPos.clone()],
    [sourcePos, targetPos]
  );

  const lineWidth = status === 'bridge' || status === 'active_path' ? 2.5 : 1.5;

  return (
    <Line
      points={points}
      color={color}
      lineWidth={lineWidth}
      opacity={status === 'failed' ? 0.3 : 1}
      transparent
      onClick={(e) => { e.stopPropagation(); onSelect(edge.id); }}
    />
  );
}

// ─── Camera Controller ────────────────────────────────────────────────────────
function CameraController({ target }: { target?: THREE.Vector3 }) {
  const { camera } = useThree();

  useEffect(() => {
    if (target) {
      const start = camera.position.clone();
      const end = target.clone().add(new THREE.Vector3(0, 0, 12));
      let t = 0;
      const animate = () => {
        t = Math.min(t + 0.03, 1);
        camera.position.lerpVectors(start, end, t);
        camera.lookAt(target);
        if (t < 1) requestAnimationFrame(animate);
      };
      animate();
    }
  }, [target, camera]);

  return null;
}

// ─── Main Scene ───────────────────────────────────────────────────────────────
export interface NetworkScene3DProps {
  nodes: CytoscapeNodeData[];
  edges: CytoscapeEdgeData[];
  nodeStates: Map<string, NodeState>;
  edgeStates: Map<string, EdgeState>;
  onNodeSelect: (id: string) => void;
  onEdgeSelect: (id: string) => void;
  cameraTarget?: THREE.Vector3;
}

function SceneContent({
  nodes,
  edges,
  nodeStates,
  edgeStates,
  onNodeSelect,
  onEdgeSelect,
  cameraTarget,
}: NetworkScene3DProps) {
  const [hoveredNode, setHoveredNode] = React.useState<string | null>(null);
  const positions = useMemo(() => computeLayout(nodes, edges), [nodes, edges]);

  const handleNodeHover = useCallback((id: string | null) => {
    setHoveredNode(id);
    document.body.style.cursor = id ? 'pointer' : 'default';
  }, []);

  useEffect(() => {
    return () => { document.body.style.cursor = 'default'; };
  }, []);

  return (
    <>
      <CameraController target={cameraTarget} />

      {/* Lighting */}
      <ambientLight intensity={0.4} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} castShadow />
      <directionalLight position={[-8, -6, -4]} intensity={0.2} color="#7DD3FC" />
      <pointLight position={[0, 8, 0]} intensity={0.3} color="#F2653A" />

      {/* Subtle grid floor */}
      <gridHelper args={[30, 30, '#1E293B', '#1E293B']} position={[0, -6, 0]} />

      {/* Edges */}
      {edges.map((edge) => {
        const sp = positions.get(edge.source);
        const tp = positions.get(edge.target);
        if (!sp || !tp) return null;
        return (
          <NetworkEdge3D
            key={edge.id}
            edge={edge}
            sourcePos={sp}
            targetPos={tp}
            edgeState={edgeStates.get(edge.id)}
            onSelect={onEdgeSelect}
          />
        );
      })}

      {/* Nodes */}
      {nodes.map((node) => {
        const pos = positions.get(node.id);
        if (!pos) return null;
        return (
          <NetworkNode3D
            key={node.id}
            node={node}
            position={pos}
            nodeState={nodeStates.get(node.id)}
            onSelect={onNodeSelect}
            onHover={handleNodeHover}
            isHovered={hoveredNode === node.id}
          />
        );
      })}

      <OrbitControls
        enableDamping
        dampingFactor={0.08}
        minDistance={4}
        maxDistance={40}
        maxPolarAngle={Math.PI * 0.85}
      />
    </>
  );
}

export const NetworkScene3D: React.FC<NetworkScene3DProps> = (props) => {
  return (
    <Canvas
      camera={{ position: [0, 0, 16], fov: 50 }}
      shadows
      style={{ background: 'transparent' }}
      gl={{ antialias: true, alpha: true }}
    >
      <SceneContent {...props} />
    </Canvas>
  );
};

