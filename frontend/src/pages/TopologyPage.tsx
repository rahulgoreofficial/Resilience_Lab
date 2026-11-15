import React, { useState, useEffect } from 'react';
import { 
  Network as NetworkIcon, 
  Plus, 
  GitFork, 
  Download, 
  Upload, 
  RefreshCw, 
  CheckCircle2, 
  Box, 
  Layers 
} from 'lucide-react';
import type { 
  Network, 
  NetworkTopologyResponse, 
  CytoscapeNodeData, 
  CytoscapeEdgeData 
} from '../types/network';
import type { ConnectivityAnalysis } from '../types/analytics';
import { CytoscapeGraph } from '../components/topology/CytoscapeGraph';
import { NetworkGraph3D } from '../components/topology/NetworkGraph3D';
import { NodeInspector } from '../components/topology/NodeInspector';
import { EdgeInspector } from '../components/topology/EdgeInspector';
import { GraphControls } from '../components/topology/GraphControls';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { computeShortestPath } from '../services/analyticsService';

export interface TopologyPageProps {
  selectedNetwork: Network | null;
  topology: NetworkTopologyResponse | null;
  analysis: ConnectivityAnalysis | null;
  onRefreshTopology: () => void;
  onSelectNodeInTopology?: (nodeId: string | null) => void;
  onAddNodeClick: () => void;
  onAddEdgeClick: () => void;
  onImportJsonClick?: () => void;
  onSimulateNodeFailure: (nodeId: string) => void;
  onSimulateEdgeFailure: (source: string, target: string) => void;
  onDeleteNode?: (nodeId: string) => void;
  onDeleteEdge?: (edgeId: string) => void;
  initialSelectedNodeId?: string | null;
}

export const TopologyPage: React.FC<TopologyPageProps> = ({
  selectedNetwork,
  topology,
  analysis,
  onRefreshTopology,
  onAddNodeClick,
  onAddEdgeClick,
  onImportJsonClick,
  onSimulateNodeFailure,
  onSimulateEdgeFailure,
  onDeleteNode,
  onDeleteEdge,
  initialSelectedNodeId
}) => {
  const [selectedNode, setSelectedNode] = useState<CytoscapeNodeData | null>(null);
  const [selectedEdge, setSelectedEdge] = useState<CytoscapeEdgeData | null>(null);
  const [layoutName, setLayoutName] = useState<'cose' | 'concentric' | 'circle' | 'breadthfirst' | 'grid'>('cose');
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
  const [highlightedPath, setHighlightedPath] = useState<string[]>([]);
  const [pathDistance, setPathDistance] = useState<number | null>(null);
  const [pathError, setPathError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Sync initial external selected node
  useEffect(() => {
    if (initialSelectedNodeId && topology) {
      const match = topology.elements.nodes.find((n) => n.data.id === initialSelectedNodeId);
      if (match) {
        setSelectedNode(match.data);
        setSelectedEdge(null);
      }
    }
  }, [initialSelectedNodeId, topology]);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefreshTopology();
    setTimeout(() => setIsRefreshing(false), 400);
  };

  const handleSelectNode = (nodeData: CytoscapeNodeData | null) => {
    setSelectedNode(nodeData);
    if (nodeData) setSelectedEdge(null);
  };

  const handleSelectEdge = (edgeData: CytoscapeEdgeData | null) => {
    setSelectedEdge(edgeData);
    if (edgeData) setSelectedNode(null);
  };

  const handleSearchNode = (nodeId: string) => {
    if (!topology) return;
    const match = topology.elements.nodes.find(
      (n) => n.data.id.toLowerCase() === nodeId.toLowerCase() || 
             n.data.label.toLowerCase().includes(nodeId.toLowerCase())
    );
    if (match) {
      setSelectedNode(match.data);
      setSelectedEdge(null);
    }
  };

  const handleFindPath = async (source: string, target: string) => {
    if (!selectedNetwork) return;
    setPathError(null);
    try {
      const res = await computeShortestPath(selectedNetwork.id, source, target);
      if (res.path && res.path.length > 0) {
        setHighlightedPath(res.path);
        setPathDistance(res.distance ?? null);
      } else {
        setPathError(`No valid communication path found between ${source} and ${target}.`);
        setHighlightedPath([]);
        setPathDistance(null);
      }
    } catch {
      setPathError(`Path calculation failed between ${source} and ${target}.`);
      setHighlightedPath([]);
      setPathDistance(null);
    }
  };

  const handleClearPath = () => {
    setHighlightedPath([]);
    setPathDistance(null);
    setPathError(null);
  };

  const handleExportJson = () => {
    if (!topology) return;
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(topology, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `${selectedNetwork?.name || 'network'}_topology.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  if (!selectedNetwork) {
    return (
      <div className="p-12 text-center bg-white/95 dark:bg-[#0D1220]/95 border border-slate-200/90 dark:border-[#253149] rounded-3xl shadow-xl max-w-4xl mx-auto my-12 text-[#171923] dark:text-[#F5F7FF]">
        <NetworkIcon className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-[#171923] dark:text-[#F5F7FF]">No Active Network Selected</h3>
        <p className="text-sm text-[#737B8C] dark:text-[#929CB3] mt-1.5">Please select an existing network or create a new network from the top bar.</p>
      </div>
    );
  }

  const allNodeIds = topology?.elements.nodes.map((n) => n.data.id) || [];
  const articulationPoints = analysis?.articulation_points || [];
  const bridgeEdgeIds = analysis?.bridges.map(([s, t]) => `${s}-${t}`) || [];

  const connectedNeighbours = selectedNode && topology
    ? topology.elements.edges
        .filter((e) => e.data.source === selectedNode.id || e.data.target === selectedNode.id)
        .map((e) => (e.data.source === selectedNode.id ? e.data.target : e.data.source))
    : [];

  return (
    <div className="space-y-4 pb-8">
      {/* Top Action & Stats Bar */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-4 sm:p-5 shadow-xs flex flex-wrap items-center justify-between gap-4 transition-colors">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#080B14] to-[#121A2B] text-[#22D3EE] flex items-center justify-center font-bold shadow-xs border border-slate-700/80 dark:border-[#253149]">
            <NetworkIcon className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">{selectedNetwork.name}</h2>
              <Badge variant="neutral">{selectedNetwork.network_type || 'undirected'}</Badge>
              <Badge variant={analysis?.is_connected ? 'healthy' : 'failed'}>
                {analysis?.is_connected ? 'Connected' : `Partitioned (${analysis?.connected_components_count ?? 1} components)`}
              </Badge>
            </div>
            <div className="flex items-center gap-3 text-xs text-[#737B8C] dark:text-[#929CB3] mt-0.5 font-mono-code">
              <span>|V| = {topology?.elements.nodes.length || selectedNetwork.node_count} nodes</span>
              <span>•</span>
              <span>|E| = {topology?.elements.edges.length || selectedNetwork.edge_count} links</span>
              <span>•</span>
              <span>Density = {((analysis?.density ?? 0) * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* 2D / 3D Visualization Switcher */}
          <div className="inline-flex rounded-xl border border-slate-200 dark:border-[#253149] bg-slate-100 dark:bg-[#121A2B] p-1 shadow-2xs">
            <button
              onClick={() => setViewMode('2d')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                viewMode === '2d' 
                  ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs border border-slate-200/80 dark:border-[#253149]' 
                  : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
              }`}
            >
              <Layers className="w-3.5 h-3.5 text-blue-600 dark:text-[#4F8CFF]" />
              2D Cytoscape
            </button>
            <button
              onClick={() => setViewMode('3d')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                viewMode === '3d' 
                  ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-xs' 
                  : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
              }`}
            >
              <Box className="w-3.5 h-3.5" />
              3D Three.js
            </button>
          </div>

          <Button
            variant="outline"
            size="sm"
            icon={<RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />}
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            Refresh
          </Button>

          {onImportJsonClick && (
            <Button
              variant="outline"
              size="sm"
              icon={<Upload className="w-3.5 h-3.5 text-indigo-600 dark:text-cyan-400" />}
              onClick={onImportJsonClick}
            >
              Import JSON
            </Button>
          )}

          <Button
            variant="outline"
            size="sm"
            icon={<Download className="w-3.5 h-3.5" />}
            onClick={handleExportJson}
          >
            Export JSON
          </Button>
          <Button
            variant="secondary"
            size="sm"
            icon={<Plus className="w-3.5 h-3.5 text-emerald-600 dark:text-[#20D6A0]" />}
            onClick={onAddNodeClick}
          >
            Add Component
          </Button>
          <Button
            variant="brand"
            size="sm"
            icon={<GitFork className="w-3.5 h-3.5" />}
            onClick={onAddEdgeClick}
          >
            Connect Link
          </Button>
        </div>
      </div>

      {/* Graph Controls Toolbar - only when in 2D layout */}
      {viewMode === '2d' && (
        <GraphControls
          layoutName={layoutName}
          onLayoutChange={setLayoutName}
          nodeIds={allNodeIds}
          onSearchNode={handleSearchNode}
          onFindPath={handleFindPath}
          onClearPath={handleClearPath}
          hasActivePath={highlightedPath.length > 0}
        />
      )}

      {/* Path calculation feedback */}
      {pathDistance !== null && (
        <div className="p-4 bg-emerald-50/90 dark:bg-emerald-950/30 border border-emerald-200/90 dark:border-emerald-500/40 rounded-2xl text-xs flex items-center justify-between shadow-2xs transition-colors">
          <div className="flex items-center gap-2 text-emerald-800 dark:text-emerald-300 font-mono-code">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600 dark:text-[#20D6A0]" />
            <span>Shortest Communication Path: <strong>{highlightedPath.join(' → ')}</strong> (Metric Distance: {pathDistance.toFixed(2)})</span>
          </div>
          <button
            onClick={handleClearPath}
            className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 underline hover:text-emerald-900 cursor-pointer"
          >
            Clear Trace
          </button>
        </div>
      )}

      {pathError && (
        <div className="p-4 bg-rose-50/90 dark:bg-rose-950/30 border border-rose-200/90 dark:border-rose-500/40 rounded-2xl text-xs text-[#FF784F] dark:text-[#FF5364] flex items-center justify-between shadow-2xs transition-colors">
          <span>{pathError}</span>
          <button
            onClick={() => setPathError(null)}
            className="text-xs underline font-semibold hover:text-rose-900 cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Main Large Workspace Canvas & Inspector */}
      <div className="relative h-[740px] bg-gradient-to-br from-[#080B14] via-[#0D1220] to-[#121A2B] rounded-3xl overflow-hidden border border-slate-800 dark:border-[#253149] shadow-2xl flex">
        {/* Canvas - Swappable between 2D Cytoscape and 3D Three.js */}
        <div className="flex-1 h-full relative">
          {viewMode === '2d' ? (
            <CytoscapeGraph
              topology={topology}
              layoutName={layoutName}
              selectedNodeId={selectedNode?.id}
              selectedEdgeId={selectedEdge?.id}
              onSelectNode={handleSelectNode}
              onSelectEdge={handleSelectEdge}
              highlightedPath={highlightedPath}
              articulationPoints={articulationPoints}
              bridgeEdgeIds={bridgeEdgeIds}
              className="w-full h-full"
            />
          ) : (
            <NetworkGraph3D
              topology={topology}
              selectedNodeId={selectedNode?.id}
              selectedEdgeId={selectedEdge?.id}
              onSelectNode={handleSelectNode}
              onSelectEdge={handleSelectEdge}
              highlightedPath={highlightedPath}
              articulationPoints={articulationPoints}
              bridgeEdgeIds={bridgeEdgeIds}
              className="w-full h-full"
            />
          )}

          {/* Floating Bottom Canvas Legend */}
          <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-2xl p-3 text-[11px] text-slate-300 font-mono-code shadow-xl pointer-events-none z-10 flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#4F8CFF] inline-block polygon-hexagon" />
              <span>Router</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#22D3EE] inline-block rounded-xs" />
              <span>Switch</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#20D6A0] inline-block rounded-full" />
              <span>Server</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#9B7BFF] inline-block" />
              <span>Database</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#F6BD60] inline-block rotate-45" />
              <span>Firewall</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-[#FF784F] inline-block rounded-xs" />
              <span>Gateway</span>
            </div>
            <div className="h-3 w-px bg-slate-700" />
            <div className="flex items-center gap-1.5 text-[#FF784F]">
              <span className="w-2 h-2 rounded-full ring-2 ring-[#FF784F] inline-block" />
              <span>Cut-Vertex (AP)</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#22D3EE]">
              <span className="w-4 h-0.5 bg-[#22D3EE] inline-block" />
              <span>Bridge Link</span>
            </div>
          </div>
        </div>

        {/* Slide-over Inspectors */}
        {selectedNode && (
          <NodeInspector
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
            onSimulateFailure={(nodeId) => onSimulateNodeFailure(nodeId)}
            onDeleteNode={onDeleteNode}
            isArticulationPoint={articulationPoints.includes(selectedNode.id)}
            connectedNeighbours={connectedNeighbours}
          />
        )}

        {selectedEdge && (
          <EdgeInspector
            edge={selectedEdge}
            onClose={() => setSelectedEdge(null)}
            onSimulateSeverance={(source, target) => onSimulateEdgeFailure(source, target)}
            onDeleteEdge={onDeleteEdge}
            isBridge={bridgeEdgeIds.includes(selectedEdge.id)}
          />
        )}
      </div>
    </div>
  );
};
