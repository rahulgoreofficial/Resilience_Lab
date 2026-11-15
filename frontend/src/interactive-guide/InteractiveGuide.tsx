/**
 * InteractiveGuide - Main container page.
 * Route: /interactive-guide (rendered via activePage === 'guide' in App.tsx)
 */

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import * as THREE from 'three';
import { Monitor, ArrowLeft, ChevronLeft, ChevronRight, AlertCircle, Loader } from 'lucide-react';

import { NetworkScene3D } from './NetworkScene3D';
import { GuideProgress } from './GuideProgress';
import { FacultyPresentationMode } from './FacultyPresentationMode';
import { Chapter1 } from './chapters/Chapter1';
import { Chapter2 } from './chapters/Chapter2';
import { Chapter3 } from './chapters/Chapter3';
import { Chapter4 } from './chapters/Chapter4';
import { Chapter5 } from './chapters/Chapter5';
import { Chapter6 } from './chapters/Chapter6';
import { CHAPTERS } from './guideConstants';

import type { GuideChapterId, NodeState, EdgeState, PresentationStep } from './guideTypes';
import type { CytoscapeNodeData, CytoscapeEdgeData } from '../types/network';
import type { ConnectivityAnalysis } from '../types/analytics';
import type { SimulationResults } from '../types/simulation';

import {
  ensureGuideNetwork,
  getTopology,
  getAnalysis,
  runNodeFailure,
  runCascadingFailure,
  addBackupEdge,
  deleteEdge,
} from './guideNetworkService';

interface Props {
  onNavigateBack: () => void;
}

// WebGL support check
function isWebGLAvailable(): boolean {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && canvas.getContext('webgl'));
  } catch { return false; }
}

export const InteractiveGuide: React.FC<Props> = ({ onNavigateBack }) => {
  const [chapter, setChapter] = useState<GuideChapterId>(1);
  const [networkId, setNetworkId] = useState<string | null>(null);
  const [nodes, setNodes] = useState<CytoscapeNodeData[]>([]);
  const [edges, setEdges] = useState<CytoscapeEdgeData[]>([]);
  const [analysis, setAnalysis] = useState<ConnectivityAnalysis | null>(null);
  const [nodeStates, setNodeStates] = useState<Map<string, NodeState>>(new Map());
  const [edgeStates, setEdgeStates] = useState<Map<string, EdgeState>>(new Map());
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [simulationResult, setSimulationResult] = useState<SimulationResults | null>(null);
  const [comparison, setComparison] = useState<{ before: SimulationResults | null; after: SimulationResults | null }>({ before: null, after: null });
  const [isRunning, setIsRunning] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showPresentation, setShowPresentation] = useState(false);
  const [cameraTarget, setCameraTarget] = useState<THREE.Vector3 | undefined>();
  const [backupEdgeId, setBackupEdgeId] = useState<string | null>(null);
  const webglAvailable = useMemo(() => isWebGLAvailable(), []);

  // Load or create guide network on mount
  useEffect(() => {
    let mounted = true;
    setIsLoading(true);
    setLoadError(null);
    ensureGuideNetwork()
      .then(({ networkId: nid, topology, analysis: an }) => {
        if (!mounted) return;
        setNetworkId(nid);
        setNodes(topology.elements.nodes.map((n) => n.data));
        setEdges(topology.elements.edges.map((e) => e.data));
        setAnalysis(an);
        setIsLoading(false);
      })
      .catch((err) => {
        if (!mounted) return;
        setLoadError(String(err?.message ?? 'Failed to load guide network. Is the backend running?'));
        setIsLoading(false);
      });
    return () => { mounted = false; };
  }, []);

  const refreshTopologyAndAnalysis = useCallback(async () => {
    if (!networkId) return;
    const [topo, an] = await Promise.all([
      getTopology(networkId),
      getAnalysis(networkId),
    ]);
    setNodes(topo.elements.nodes.map((n) => n.data));
    setEdges(topo.elements.edges.map((e) => e.data));
    setAnalysis(an);
  }, [networkId]);

  // Node selection handler
  const handleNodeSelect = useCallback((id: string) => {
    setSelectedNodeId((prev) => prev === id ? null : id);
    setSelectedEdgeId(null);
    setNodeStates((prev) => {
      const next = new Map(prev);
      // Clear previous selection
      for (const [k, v] of next) {
        if (v.status === 'selected') next.set(k, { ...v, status: 'healthy' });
      }
      if (prev.get(id)?.status !== 'selected') {
        next.set(id, { ...(next.get(id) ?? { id }), status: 'selected' });
      }
      return next;
    });
  }, []);

  const handleEdgeSelect = useCallback((id: string) => {
    setSelectedEdgeId((prev) => prev === id ? null : id);
    setSelectedNodeId(null);
  }, []);

  // Chapter 3 — highlight articulation points
  const highlightArticulationPoints = useCallback(() => {
    if (!analysis) return;
    setNodeStates(() => {
      const m = new Map<string, NodeState>();
      for (const n of nodes) {
        m.set(n.id, {
          id: n.id,
          status: analysis.articulation_points.includes(n.id) ? 'critical' : 'healthy',
          isArticulationPoint: analysis.articulation_points.includes(n.id),
        });
      }
      return m;
    });
  }, [analysis, nodes]);

  const highlightBridges = useCallback(() => {
    if (!analysis) return;
    const bridgeSet = new Set(analysis.bridges.flatMap(([s, t]) => {
      const e = edges.find((ed) => (ed.source === s && ed.target === t) || (ed.source === t && ed.target === s));
      return e ? [e.id] : [];
    }));
    setEdgeStates(() => {
      const m = new Map<string, EdgeState>();
      for (const e of edges) {
        m.set(e.id, { id: e.id, status: bridgeSet.has(e.id) ? 'bridge' : 'healthy' });
      }
      return m;
    });
    setNodeStates((prev) => {
      const m = new Map(prev);
      for (const e of edges) {
        if (bridgeSet.has(e.id)) {
          m.set(e.source, { ...(m.get(e.source) ?? { id: e.source }), status: 'highlighted' });
          m.set(e.target, { ...(m.get(e.target) ?? { id: e.target }), status: 'highlighted' });
        }
      }
      return m;
    });
  }, [analysis, edges]);

  // Chapter 4 — run node failure
  const handleRunFailure = useCallback(async (nodeIds: string[]) => {
    if (!networkId) return;
    setIsRunning(true);
    try {
      const result = await runNodeFailure(networkId, nodeIds);
      setSimulationResult(result);

      const failedSet = new Set(result.failed_nodes ?? []);
      const isolatedSet = new Set((result.isolated_nodes ?? []).map(String));

      setNodeStates(() => {
        const m = new Map<string, NodeState>();
        for (const n of nodes) {
          const nid = n.id;
          let status: NodeState['status'] = 'healthy';
          if (failedSet.has(nid)) status = 'failed';
          else if (isolatedSet.has(nid)) status = 'disconnected';
          m.set(nid, { id: nid, status });
        }
        return m;
      });
    } finally {
      setIsRunning(false);
    }
  }, [networkId, nodes]);

  // Chapter 5 — run cascading failure
  const handleRunCascading = useCallback(async (nodeId: string, threshold: number, maxRounds: number) => {
    if (!networkId) return;
    setIsRunning(true);
    try {
      const result = await runCascadingFailure(networkId, [nodeId], threshold, maxRounds);
      setSimulationResult(result);

      const failedSet = new Set((result.failed_nodes ?? []).map(String));
      setNodeStates(() => {
        const m = new Map<string, NodeState>();
        for (const n of nodes) {
          m.set(n.id, { id: n.id, status: failedSet.has(n.id) ? 'failed' : 'healthy' });
        }
        return m;
      });
    } finally {
      setIsRunning(false);
    }
  }, [networkId, nodes]);

  // Chapter 6 — add backup edge
  const handleAddBackupLink = useCallback(async (source: string, target: string) => {
    if (!networkId) return;
    const eid = `backup-${source}-${target}-${Date.now()}`;
    await addBackupEdge(networkId, eid, source, target);
    setBackupEdgeId(eid);
    await refreshTopologyAndAnalysis();
  }, [networkId, refreshTopologyAndAnalysis]);

  // Chapter 6 — run before/after comparison
  const handleRunComparison = useCallback(async (failedNodeId: string) => {
    if (!networkId) return;
    setIsRunning(true);
    try {
      // BEFORE: run failure on current graph (backup already added if user did step 1)
      // We need to simulate before by temporarily removing the backup
      let before: SimulationResults;
      let after: SimulationResults;

      if (backupEdgeId) {
        // Remove backup, run before, re-add backup, run after
        await deleteEdge(networkId, backupEdgeId);
        await refreshTopologyAndAnalysis();
        before = await runNodeFailure(networkId, [failedNodeId]);
        // re-add backup
        const parts = backupEdgeId.replace('backup-', '').split('-');
        const src = parts[0], tgt = parts[1];
        await addBackupEdge(networkId, backupEdgeId, src, tgt);
        await refreshTopologyAndAnalysis();
        after = await runNodeFailure(networkId, [failedNodeId]);
      } else {
        // No backup added yet — run same simulation twice as placeholder
        before = await runNodeFailure(networkId, [failedNodeId]);
        after = before;
      }

      setComparison({ before, after });

      // Show after state in 3D
      const failedSet = new Set((after.failed_nodes ?? []).map(String));
      const isolatedSet = new Set((after.isolated_nodes ?? []).map(String));
      setNodeStates(() => {
        const m = new Map<string, NodeState>();
        for (const n of nodes) {
          let status: NodeState['status'] = 'healthy';
          if (failedSet.has(n.id)) status = 'failed';
          else if (isolatedSet.has(n.id)) status = 'disconnected';
          m.set(n.id, { id: n.id, status });
        }
        return m;
      });
    } finally {
      setIsRunning(false);
    }
  }, [networkId, backupEdgeId, nodes, refreshTopologyAndAnalysis]);

  // Reset all states
  const handleReset = useCallback(() => {
    setNodeStates(new Map());
    setEdgeStates(new Map());
    setSimulationResult(null);
    setSelectedNodeId(null);
    setSelectedEdgeId(null);
    setComparison({ before: null, after: null });
  }, []);

  // Chapter navigation
  const goToChapter = useCallback((id: GuideChapterId) => {
    setChapter(id);
    handleReset();
  }, [handleReset]);

  // Faculty presentation mode handlers
  const handlePresentationStep = useCallback((step: PresentationStep) => {
    if (step.autoAction === 'show_articulation') highlightArticulationPoints();
    else if (step.autoAction === 'show_bridges') highlightBridges();
    if (step.cameraTarget) setCameraTarget(new THREE.Vector3(...step.cameraTarget));
  }, [highlightArticulationPoints, highlightBridges]);

  const currentChapterData = CHAPTERS.find((c) => c.id === chapter)!;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[500px] flex-col gap-3">
        <Loader className="w-8 h-8 text-[#F2653A] animate-spin" />
        <p className="text-sm text-[#475569]">Loading Interactive 3D Network Lab…</p>
        <p className="text-xs text-[#94A3B8]">Creating demonstration network on backend…</p>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="flex items-center justify-center h-full min-h-[500px] flex-col gap-3">
        <AlertCircle className="w-8 h-8 text-[#EF4444]" />
        <p className="text-sm font-semibold text-[#EF4444]">Failed to load guide</p>
        <p className="text-xs text-[#475569] max-w-sm text-center">{loadError}</p>
        <button onClick={onNavigateBack} className="text-xs text-[#F2653A] underline cursor-pointer">Go back</button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full min-h-[calc(100vh-6rem)] bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md rounded-3xl border border-slate-200/80 dark:border-[#253149] shadow-xl overflow-hidden">
      {/* Guide Header */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border-b border-slate-100 dark:border-[#253149] px-6 py-4 flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={onNavigateBack}
            className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF] cursor-pointer transition-colors bg-slate-50 dark:bg-[#121A2B] hover:bg-slate-100 dark:hover:bg-[#182238] px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-[#253149]"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Dashboard
          </button>
          <div className="h-5 w-px bg-slate-200 dark:bg-[#253149]" />
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-black text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                INTERACTIVE 3D NETWORK LAB
              </h1>
              <span className="text-[10px] font-mono-code font-bold uppercase bg-cyan-50 dark:bg-cyan-950/40 text-cyan-700 dark:text-cyan-300 px-2 py-0.5 rounded-full border border-cyan-200 dark:border-cyan-800/40">
                Immersive Guide
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-[#929CB3] font-medium">
              {currentChapterData.icon} Chapter {chapter}: {currentChapterData.title}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <GuideProgress currentChapter={chapter} onNavigate={goToChapter} />
          <button
            onClick={() => setShowPresentation(!showPresentation)}
            className={`flex items-center gap-2 text-xs px-3.5 py-1.5 rounded-xl font-bold border cursor-pointer transition-all ${
              showPresentation
                ? 'bg-gradient-to-r from-indigo-600 to-blue-600 text-white shadow-md border-transparent'
                : 'bg-white dark:bg-[#121A2B] text-slate-700 dark:text-[#F5F7FF] border-slate-200/90 dark:border-[#253149] hover:bg-slate-50 dark:hover:bg-[#182238] shadow-2xs'
            }`}
          >
            <Monitor className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Faculty Presentation Mode</span>
          </button>
        </div>
      </div>

      {/* Main content: 3D Canvas + Explanation Panel */}
      <div className="flex-1 flex flex-col lg:flex-row gap-0 overflow-hidden">
        {/* 3D Canvas */}
        <div className="flex-1 bg-gradient-to-br from-[#080E1C] via-[#0F172A] to-[#0A1225] relative min-h-[440px]">
          {webglAvailable ? (
            <NetworkScene3D
              nodes={nodes}
              edges={edges}
              nodeStates={nodeStates}
              edgeStates={edgeStates}
              onNodeSelect={handleNodeSelect}
              onEdgeSelect={handleEdgeSelect}
              cameraTarget={cameraTarget}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-white flex-col gap-3 p-8">
              <AlertCircle className="w-8 h-8 text-[#F59E0B]" />
              <p className="text-sm font-semibold">WebGL not available</p>
              <p className="text-xs text-[#94A3B8] text-center">Your browser doesn't support WebGL. Please use Chrome, Firefox, or Edge for the 3D experience.</p>
              {/* 2D Fallback Table */}
              <div className="w-full max-w-sm mt-4">
                <table className="w-full text-xs border-collapse">
                  <thead>
                    <tr className="text-[#94A3B8] border-b border-[#1E293B]">
                      <th className="text-left py-1 px-2">Node</th>
                      <th className="text-left py-1 px-2">Type</th>
                      <th className="text-left py-1 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {nodes.map((n) => (
                      <tr key={n.id} className="border-b border-[#1E293B]">
                        <td className="py-1 px-2 font-mono text-white">{n.id}</td>
                        <td className="py-1 px-2 text-[#94A3B8]">{n.node_type}</td>
                        <td className="py-1 px-2">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                            nodeStates.get(n.id)?.status === 'failed' ? 'bg-red-900 text-red-300' : 'bg-green-900 text-green-300'
                          }`}>
                            {nodeStates.get(n.id)?.status ?? 'healthy'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Network stats overlay */}
          <div className="absolute top-3 left-3 bg-[#0B1120]/80 backdrop-blur-sm border border-[#1E293B] rounded-lg px-3 py-2 text-[11px] font-mono space-y-0.5">
            <p className="text-[#22D3EE]">Guide Demo Network</p>
            <p className="text-[#94A3B8]">|V| = {nodes.length} nodes  |E| = {edges.length} edges</p>
            {analysis && (
              <p className="text-[#94A3B8]">
                {analysis.is_connected ? '✓ Connected' : '⚠ Partitioned'} · {analysis.connected_components_count} component{analysis.connected_components_count !== 1 ? 's' : ''}
              </p>
            )}
          </div>

          {/* Selected info overlay */}
          {(selectedNodeId || selectedEdgeId) && (
            <div className="absolute bottom-3 left-3 bg-[#0B1120]/90 backdrop-blur-sm border border-[#22D3EE]/30 rounded-lg px-3 py-2 text-[11px] font-mono max-w-[220px]">
              {selectedNodeId && (
                <div className="space-y-0.5">
                  <p className="text-[#22D3EE] font-bold">NODE: {selectedNodeId}</p>
                  {nodes.find(n => n.id === selectedNodeId) && (() => {
                    const n = nodes.find(n => n.id === selectedNodeId)!;
                    return <>
                      <p className="text-[#94A3B8]">Type: {n.node_type}</p>
                      <p className="text-[#94A3B8]">Capacity: {n.capacity?.toFixed(0)}</p>
                      <p className="text-[#94A3B8]">Load: {((n.current_load ?? 0) * 100).toFixed(0)}%</p>
                      {analysis?.articulation_points.includes(selectedNodeId) && (
                        <p className="text-[#F59E0B]">⚠ Articulation Point</p>
                      )}
                    </>;
                  })()}
                </div>
              )}
              {selectedEdgeId && (() => {
                const e = edges.find(ed => ed.id === selectedEdgeId);
                if (!e) return null;
                return (
                  <div className="space-y-0.5">
                    <p className="text-[#22D3EE] font-bold">EDGE: {selectedEdgeId}</p>
                    <p className="text-[#94A3B8]">{e.source} ↔ {e.target}</p>
                    <p className="text-[#94A3B8]">Weight: {e.weight} | Latency: {e.latency}ms</p>
                    {analysis?.bridges.some(([s, t]) =>
                      (s === e.source && t === e.target) || (s === e.target && t === e.source)
                    ) && <p className="text-[#F59E0B]">⚠ Bridge</p>}
                  </div>
                );
              })()}
            </div>
          )}
        </div>

        {/* Explanation Panel */}
        <div className="w-full lg:w-[380px] bg-white dark:bg-[#0D1220] border-l border-slate-200/80 dark:border-[#253149] p-4 overflow-y-auto max-h-[calc(100vh-10rem)]">
          {chapter === 1 && (
            <Chapter1 nodes={nodes} selectedNodeId={selectedNodeId} />
          )}
          {chapter === 2 && (
            <Chapter2 nodes={nodes} edges={edges} selectedEdgeId={selectedEdgeId} selectedNodeId={selectedNodeId} />
          )}
          {chapter === 3 && (
            <Chapter3
              nodes={nodes}
              analysis={analysis}
              selectedNodeId={selectedNodeId}
              onHighlightArticulationPoints={highlightArticulationPoints}
              onHighlightBridges={highlightBridges}
            />
          )}
          {chapter === 4 && (
            <Chapter4
              nodes={nodes}
              onRunFailure={handleRunFailure}
              onReset={handleReset}
              simulationResult={simulationResult}
              isRunning={isRunning}
            />
          )}
          {chapter === 5 && (
            <Chapter5
              nodes={nodes}
              onRunCascading={handleRunCascading}
              onReset={handleReset}
              simulationResult={simulationResult}
              isRunning={isRunning}
            />
          )}
          {chapter === 6 && (
            <Chapter6
              nodes={nodes}
              onAddBackupLink={handleAddBackupLink}
              onRunComparison={handleRunComparison}
              onReset={handleReset}
              comparison={comparison}
              isRunning={isRunning}
            />
          )}
        </div>
      </div>

      {/* Chapter navigation footer */}
      <div className="bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border-t border-slate-100 dark:border-[#253149] px-6 py-4 flex items-center justify-between">
        <button
          onClick={() => goToChapter(Math.max(1, chapter - 1) as GuideChapterId)}
          disabled={chapter === 1}
          className="flex items-center gap-2 text-xs font-semibold text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF] disabled:opacity-30 cursor-pointer bg-slate-50 dark:bg-[#121A2B] hover:bg-slate-100 dark:hover:bg-[#182238] px-3.5 py-2 rounded-xl border border-slate-200 dark:border-[#253149] transition-colors"
        >
          <ChevronLeft className="w-4 h-4" /> Previous Chapter
        </button>

        <div className="text-xs font-mono-code font-bold text-slate-500 dark:text-[#69758E]">
          Chapter {chapter} of {CHAPTERS.length} — <span className="text-slate-900 dark:text-[#F5F7FF]">{currentChapterData.title}</span>
        </div>

        <button
          onClick={() => goToChapter(Math.min(6, chapter + 1) as GuideChapterId)}
          disabled={chapter === 6}
          className="flex items-center gap-2 text-xs font-bold text-white bg-gradient-to-r from-[#6366F1] via-[#3B82F6] to-[#22D3EE] hover:brightness-105 disabled:opacity-30 cursor-pointer px-4 py-2 rounded-xl shadow-xs transition-all"
        >
          Next Chapter <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {/* Faculty Presentation Mode overlay */}
      {showPresentation && (
        <FacultyPresentationMode
          onClose={() => setShowPresentation(false)}
          onStepChange={handlePresentationStep}
          onNavigateChapter={goToChapter}
        />
      )}
    </div>
  );
};

