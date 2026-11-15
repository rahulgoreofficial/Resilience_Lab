import React, { useState } from 'react';
import { 
  Play, 
  RotateCcw, 
  Zap, 
  Sliders, 
  Target, 
  Shuffle, 
  Layers,
  Server,
  Info
} from 'lucide-react';
import type { SimulationType } from '../../types/simulation';
import type { NetworkTopologyResponse } from '../../types/network';
import { Button } from '../common/Button';

export interface SimulationFormsProps {
  topology: NetworkTopologyResponse | null;
  onRunNodeFailure: (failedNodeIds: string[]) => void;
  onRunEdgeFailure: (failedEdges: Array<[string, string]>) => void;
  onRunMultipleFailure: (failedNodeIds: string[], failedEdges: Array<[string, string]>) => void;
  onRunRandomFailure: (count: number, numTrials: number, seed: number) => void;
  onRunTargetedFailure: (strategy: 'degree' | 'articulation_points' | 'impact', count: number, adaptive: boolean) => void;
  onRunCascadingFailure: (initialFailedNodes: string[], overloadThreshold: number, maxRounds: number) => void;
  onReset: () => void;
  isLoading: boolean;
}

export const SimulationForms: React.FC<SimulationFormsProps> = ({
  topology,
  onRunNodeFailure,
  onRunEdgeFailure,
  onRunMultipleFailure,
  onRunRandomFailure,
  onRunTargetedFailure,
  onRunCascadingFailure,
  onReset,
  isLoading
}) => {
  const [activeTab, setActiveTab] = useState<SimulationType>('node_failure');

  // Node Failure state
  const [selectedNodeIds, setSelectedNodeIds] = useState<string[]>([]);

  // Edge Failure state
  const [selectedEdgeIds, setSelectedEdgeIds] = useState<string[]>([]);

  // Random Failure state
  const [randomCount, setRandomCount] = useState<number>(3);
  const [randomTrials, setRandomTrials] = useState<number>(50);
  const [randomSeed, setRandomSeed] = useState<number>(42);

  // Targeted Failure state
  const [targetedStrategy, setTargetedStrategy] = useState<'degree' | 'articulation_points' | 'impact'>('degree');
  const [targetedCount, setTargetedCount] = useState<number>(2);
  const [adaptive, setAdaptive] = useState<boolean>(true);

  // Cascading Failure state
  const [cascadeInitialNodes, setCascadeInitialNodes] = useState<string[]>([]);
  const [overloadThreshold, setOverloadThreshold] = useState<number>(1.2);
  const [maxRounds, setMaxRounds] = useState<number>(10);

  const availableNodes = topology?.nodes || [];
  const availableEdges = topology?.edges || [];

  const handleToggleNode = (id: string, list: string[], setList: (l: string[]) => void) => {
    if (list.includes(id)) {
      setList(list.filter((x) => x !== id));
    } else {
      setList([...list, id]);
    }
  };

  const handleToggleEdge = (id: string) => {
    if (selectedEdgeIds.includes(id)) {
      setSelectedEdgeIds(selectedEdgeIds.filter((x) => x !== id));
    } else {
      setSelectedEdgeIds([...selectedEdgeIds, id]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'node_failure') {
      if (selectedNodeIds.length === 0) return;
      onRunNodeFailure(selectedNodeIds);
    } else if (activeTab === 'edge_failure') {
      if (selectedEdgeIds.length === 0) return;
      const edgePairs: Array<[string, string]> = selectedEdgeIds
        .map((eId) => availableEdges.find((e) => e.edge_id === eId))
        .filter((e): e is typeof availableEdges[0] => Boolean(e))
        .map((e) => [e.source_node_id, e.target_node_id]);
      onRunEdgeFailure(edgePairs);
    } else if (activeTab === 'multiple_failure') {
      const edgePairs: Array<[string, string]> = selectedEdgeIds
        .map((eId) => availableEdges.find((e) => e.edge_id === eId))
        .filter((e): e is typeof availableEdges[0] => Boolean(e))
        .map((e) => [e.source_node_id, e.target_node_id]);
      onRunMultipleFailure(selectedNodeIds, edgePairs);
    } else if (activeTab === 'random') {
      onRunRandomFailure(randomCount, randomTrials, randomSeed);
    } else if (activeTab === 'targeted') {
      onRunTargetedFailure(targetedStrategy, targetedCount, adaptive);
    } else if (activeTab === 'cascading') {
      if (cascadeInitialNodes.length === 0) return;
      onRunCascadingFailure(cascadeInitialNodes, overloadThreshold, maxRounds);
    }
  };

  const tabs: Array<{ id: SimulationType; label: string; icon: React.ReactNode }> = [
    { id: 'node_failure', label: 'Node Failure', icon: <Server className="w-3.5 h-3.5" /> },
    { id: 'edge_failure', label: 'Edge Severance', icon: <Sliders className="w-3.5 h-3.5" /> },
    { id: 'multiple_failure', label: 'Multi-Component', icon: <Layers className="w-3.5 h-3.5" /> },
    { id: 'random', label: 'Random (Monte Carlo)', icon: <Shuffle className="w-3.5 h-3.5" /> },
    { id: 'targeted', label: 'Targeted Attack', icon: <Target className="w-3.5 h-3.5" /> },
    { id: 'cascading', label: 'Cascading Overload', icon: <Zap className="w-3.5 h-3.5" /> },
  ];

  return (
    <div className="bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-3xl shadow-sm overflow-hidden flex flex-col text-[#171923] dark:text-[#F5F7FF] transition-colors">
      {/* Header */}
      <div className="px-6 py-4.5 border-b border-slate-100 dark:border-[#253149] bg-slate-50/60 dark:bg-[#121A2B]/70">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Disruption Experiment Setup</h3>
            <p className="text-xs text-[#737B8C] dark:text-[#929CB3] mt-0.5">Select mathematical failure model and configure parameters</p>
          </div>
          <button
            type="button"
            onClick={onReset}
            className="text-xs text-slate-500 dark:text-[#929CB3] hover:text-slate-800 dark:hover:text-[#F5F7FF] flex items-center gap-1 font-mono-code font-medium cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Mode Tabs (Unclippable, flexible wrapped pill navigation) */}
      <div className="p-3 bg-slate-100/70 dark:bg-[#121A2B]/80 border-b border-slate-200/80 dark:border-[#253149] flex flex-wrap gap-1.5">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold cursor-pointer transition-all ${
                isActive
                  ? 'bg-white dark:bg-[#182238] text-indigo-700 dark:text-cyan-400 shadow-xs border border-indigo-200/80 dark:border-[#253149]'
                  : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF] hover:bg-white/50 dark:hover:bg-[#182238]/60 border border-transparent'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Form Content */}
      <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1 flex flex-col justify-between">
        <div className="space-y-5">
          {/* Node Failure Mode */}
          {activeTab === 'node_failure' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#171923] font-mono-code uppercase tracking-wider">
                  Select Nodes to Inactivate ({selectedNodeIds.length} chosen)
                </label>
                {selectedNodeIds.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setSelectedNodeIds([])}
                    className="text-[11px] text-[#F2653A] font-semibold hover:underline cursor-pointer"
                  >
                    Clear All
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-56 overflow-y-auto p-2.5 bg-slate-50 border border-slate-200/90 rounded-2xl">
                {availableNodes.map((n) => {
                  const isSelected = selectedNodeIds.includes(n.node_id);
                  return (
                    <button
                      key={n.node_id}
                      type="button"
                      onClick={() => handleToggleNode(n.node_id, selectedNodeIds, setSelectedNodeIds)}
                      className={`p-2.5 rounded-xl text-xs font-mono-code text-left border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-rose-50 border-[#F2653A] text-[#F2653A] font-bold shadow-2xs'
                          : 'bg-white border-slate-200 text-slate-800 hover:border-slate-300'
                      }`}
                    >
                      <div className="truncate font-semibold">{n.node_id}</div>
                      <div className="text-[10px] text-slate-400 uppercase">{n.node_type}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Edge Failure Mode */}
          {activeTab === 'edge_failure' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-[#171923] font-mono-code uppercase tracking-wider">
                  Select Cable Links to Sever ({selectedEdgeIds.length} chosen)
                </label>
                {selectedEdgeIds.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setSelectedEdgeIds([])}
                    className="text-[11px] text-[#F2653A] font-semibold hover:underline cursor-pointer"
                  >
                    Clear All
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2 max-h-56 overflow-y-auto p-2.5 bg-slate-50 border border-slate-200/90 rounded-2xl">
                {availableEdges.map((e) => {
                  const isSelected = selectedEdgeIds.includes(e.edge_id);
                  return (
                    <button
                      key={e.edge_id}
                      type="button"
                      onClick={() => handleToggleEdge(e.edge_id)}
                      className={`p-2.5 rounded-xl text-xs font-mono-code text-left border cursor-pointer transition-all ${
                        isSelected
                          ? 'bg-rose-50 border-[#F2653A] text-[#F2653A] font-bold shadow-2xs'
                          : 'bg-white border-slate-200 text-slate-800 hover:border-slate-300'
                      }`}
                    >
                      <div className="truncate font-semibold">{e.source_node_id} &harr; {e.target_node_id}</div>
                      <div className="text-[10px] text-slate-400">W: {e.weight} · {e.capacity}G</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Multiple Failure Mode */}
          {activeTab === 'multiple_failure' && (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-bold text-[#171923] font-mono-code uppercase tracking-wider">
                  Targeted Vertices ({selectedNodeIds.length})
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 border border-slate-200/90 rounded-xl">
                  {availableNodes.map((n) => {
                    const isSelected = selectedNodeIds.includes(n.node_id);
                    return (
                      <button
                        key={n.node_id}
                        type="button"
                        onClick={() => handleToggleNode(n.node_id, selectedNodeIds, setSelectedNodeIds)}
                        className={`p-1.5 rounded-lg text-xs font-mono-code text-left border cursor-pointer transition-all ${
                          isSelected ? 'bg-rose-50 border-[#F2653A] text-[#F2653A] font-bold' : 'bg-white border-slate-200 text-slate-700'
                        }`}
                      >
                        <span className="truncate">{n.node_id}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-bold text-[#171923] font-mono-code uppercase tracking-wider">
                  Targeted Links ({selectedEdgeIds.length})
                </label>
                <div className="grid grid-cols-2 gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 border border-slate-200/90 rounded-xl">
                  {availableEdges.map((e) => {
                    const isSelected = selectedEdgeIds.includes(e.edge_id);
                    return (
                      <button
                        key={e.edge_id}
                        type="button"
                        onClick={() => handleToggleEdge(e.edge_id)}
                        className={`p-1.5 rounded-lg text-xs font-mono-code text-left border cursor-pointer transition-all ${
                          isSelected ? 'bg-rose-50 border-[#F2653A] text-[#F2653A] font-bold' : 'bg-white border-slate-200 text-slate-700'
                        }`}
                      >
                        <span className="truncate">{e.source_node_id}-{e.target_node_id}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* Random Monte Carlo Mode */}
          {activeTab === 'random' && (
            <div className="space-y-4">
              <div className="p-3 bg-cyan-50/80 border border-cyan-200/80 rounded-2xl flex items-start gap-2.5 text-xs text-cyan-900">
                <Info className="w-4 h-4 text-cyan-600 shrink-0 mt-0.5" />
                <span>Simulates hardware wear-out or random power outages using Monte Carlo randomized sampling.</span>
              </div>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-xs font-semibold font-mono-code mb-1">
                    <span>Simultaneous Failures:</span>
                    <span className="text-cyan-700 font-bold">{randomCount} nodes</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max={Math.max(2, availableNodes.length - 1)}
                    value={randomCount}
                    onChange={(e) => setRandomCount(parseInt(e.target.value, 10))}
                    className="w-full accent-cyan-600 cursor-pointer"
                  />
                </div>
                <div>
                  <div className="flex justify-between text-xs font-semibold font-mono-code mb-1">
                    <span>Monte Carlo Trials:</span>
                    <span className="text-cyan-700 font-bold">{randomTrials} runs</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="200"
                    step="10"
                    value={randomTrials}
                    onChange={(e) => setRandomTrials(parseInt(e.target.value, 10))}
                    className="w-full accent-cyan-600 cursor-pointer"
                  />
                </div>
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 font-mono-code uppercase block mb-1">Random Seed</label>
                  <input
                    type="number"
                    value={randomSeed}
                    onChange={(e) => setRandomSeed(parseInt(e.target.value, 10))}
                    className="w-full bg-slate-50 border border-slate-200/90 rounded-xl px-3 py-2 text-xs font-mono-code text-slate-800 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Targeted Failure Mode */}
          {activeTab === 'targeted' && (
            <div className="space-y-4">
              <div className="p-3 bg-indigo-50/80 border border-indigo-200/80 rounded-2xl flex items-start gap-2.5 text-xs text-indigo-900">
                <Info className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                <span>Simulates targeted adversarial attacks aiming to maximize topological fragmentation.</span>
              </div>
              <div className="space-y-3">
                <div>
                  <label className="text-[11px] font-semibold text-slate-500 font-mono-code uppercase block mb-1">Targeting Strategy</label>
                  <select
                    value={targetedStrategy}
                    onChange={(e) => setTargetedStrategy(e.target.value as any)}
                    className="w-full bg-slate-50 border border-slate-200/90 rounded-xl px-3 py-2 text-xs font-mono-code text-slate-800 focus:outline-none cursor-pointer"
                  >
                    <option value="degree">Highest Degree Hubs (max links)</option>
                    <option value="articulation_points">Cut-Vertices / Single Points of Failure</option>
                    <option value="impact">Eigenvector / Betweenness Criticality</option>
                  </select>
                </div>
                <div>
                  <div className="flex justify-between text-xs font-semibold font-mono-code mb-1">
                    <span>Attack Depth (Nodes Targeted):</span>
                    <span className="text-indigo-600 font-bold">{targetedCount} nodes</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max={Math.max(2, Math.floor(availableNodes.length / 2))}
                    value={targetedCount}
                    onChange={(e) => setTargetedCount(parseInt(e.target.value, 10))}
                    className="w-full accent-indigo-600 cursor-pointer"
                  />
                </div>
                <div className="flex items-center gap-2 pt-1">
                  <input
                    type="checkbox"
                    id="adaptiveCheck"
                    checked={adaptive}
                    onChange={(e) => setAdaptive(e.target.checked)}
                    className="rounded accent-indigo-600 cursor-pointer"
                  />
                  <label htmlFor="adaptiveCheck" className="text-xs text-slate-700 font-medium cursor-pointer">
                    Adaptive recalculated centralities after each attack round
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Cascading Failure Mode */}
          {activeTab === 'cascading' && (
            <div className="space-y-4">
              <div className="p-3 bg-amber-50/80 border border-amber-200/80 rounded-2xl flex items-start gap-2.5 text-xs text-amber-900">
                <Zap className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <span>Simulates nonlinear traffic redistribution and cascading overload propagation across surviving paths.</span>
              </div>
              <div className="space-y-3">
                <label className="text-[11px] font-semibold text-slate-500 font-mono-code uppercase block">
                  Select Initial Outage Trigger ({cascadeInitialNodes.length})
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-32 overflow-y-auto p-2 bg-slate-50 border border-slate-200/90 rounded-xl">
                  {availableNodes.map((n) => {
                    const isSelected = cascadeInitialNodes.includes(n.node_id);
                    return (
                      <button
                        key={n.node_id}
                        type="button"
                        onClick={() => handleToggleNode(n.node_id, cascadeInitialNodes, setCascadeInitialNodes)}
                        className={`p-1.5 rounded-lg text-xs font-mono-code text-left border cursor-pointer transition-all ${
                          isSelected ? 'bg-amber-100 border-amber-500 text-amber-800 font-bold' : 'bg-white border-slate-200 text-slate-700'
                        }`}
                      >
                        <span className="truncate">{n.node_id}</span>
                      </button>
                    );
                  })}
                </div>
                <div>
                  <div className="flex justify-between text-xs font-semibold font-mono-code mb-1">
                    <span>Overload Trip Threshold (&alpha;):</span>
                    <span className="text-amber-700 font-bold">{(overloadThreshold * 100).toFixed(0)}% capacity</span>
                  </div>
                  <input
                    type="range"
                    min="1.0"
                    max="2.0"
                    step="0.05"
                    value={overloadThreshold}
                    onChange={(e) => setOverloadThreshold(parseFloat(e.target.value))}
                    className="w-full accent-amber-600 cursor-pointer"
                  />
                </div>
                <div>
                  <div className="flex justify-between text-xs font-semibold font-mono-code mb-1">
                    <span>Max Propagation Rounds:</span>
                    <span className="text-amber-700 font-bold">{maxRounds} rounds</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="25"
                    step="1"
                    value={maxRounds}
                    onChange={(e) => setMaxRounds(parseInt(e.target.value, 10))}
                    className="w-full accent-amber-600 cursor-pointer"
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Execution Button */}
        <div className="pt-4 border-t border-slate-100">
          <Button
            type="submit"
            variant="brand"
            size="lg"
            className="w-full font-bold tracking-tight shadow-md"
            icon={<Play className="w-4 h-4 text-white" />}
            isLoading={isLoading}
          >
            EXECUTE SIMULATION
          </Button>
        </div>
      </form>
    </div>
  );
};
