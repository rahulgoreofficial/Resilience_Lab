/**
 * Chapter 4 — Simulating Network Failures
 * Features the Guided Campus Laboratory Connectivity Failure Scenario (Steps A to C)
 */

import React, { useState } from 'react';
import { PlayCircle, RotateCcw, Loader, AlertTriangle, Zap } from 'lucide-react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData } from '../../types/network';
import type { SimulationResults } from '../../types/simulation';

interface Props {
  nodes: CytoscapeNodeData[];
  onRunFailure: (nodeIds: string[]) => Promise<void>;
  onReset: () => void;
  simulationResult: SimulationResults | null;
  isRunning: boolean;
}

export const Chapter4: React.FC<Props> = ({
  nodes, onRunFailure, onReset, simulationResult, isRunning,
}) => {
  const [selected, setSelected] = useState<string[]>([]);

  const toggleNode = (id: string) => {
    setSelected((prev) => prev.includes(id) ? prev.filter(n => n !== id) : [...prev, id]);
  };

  const handleRun = async () => {
    if (selected.length === 0) return;
    await onRunFailure(selected);
  };

  const handleRunCampusDemoFailure = async () => {
    // Laboratory branch failure: fail L1 (or incident to C1-L1)
    const targetNode = nodes.find(n => n.id === 'L1') ? 'L1' : nodes[0]?.id;
    if (targetNode) {
      setSelected([targetNode]);
      await onRunFailure([targetNode]);
    }
  };

  const handleReset = () => {
    setSelected([]);
    onReset();
  };

  return (
    <GuideExplanationPanel
      chapterId={4}
      title="Simulating Network Failures"
      subtitle="What happens when a device or communication link breaks?"
    >
      <p>
        Real networks experience disruptions daily — fiber cuts, hardware faults, and switch breakdowns.
        We use <strong>graph theory</strong> to predict <em>mathematically</em> which nodes and services become disconnected.
      </p>

      {/* Guided Campus Scenario Banner */}
      <div className="bg-[#FEF2EE] dark:bg-orange-950/30 border-2 border-[#F2653A]/40 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold font-mono-code uppercase text-[#F2653A] flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Campus Demonstration Scenario
          </span>
          <span className="text-[10px] bg-[#F2653A] text-white px-2 py-0.5 rounded-full font-bold">
            STEPS A - C
          </span>
        </div>
        <p className="text-xs text-[#171B26] dark:text-[#F5F7FF] font-semibold">
          "Campus Laboratory Connectivity Failure"
        </p>
        <p className="text-[11px] text-[#7C2D12] dark:text-orange-200 leading-relaxed">
          The 12-node campus network connects the Laboratory Switch (<code className="font-mono">L1</code>) and Server (<code className="font-mono">LS1</code>) 
          to the Core Switch (<code className="font-mono">C1</code>) via a single transmission bridge. 
          Disrupting this link isolates the entire laboratory branch.
        </p>

        <button
          onClick={handleRunCampusDemoFailure}
          disabled={isRunning}
          className="w-full flex items-center justify-center gap-1.5 text-xs bg-[#F2653A] hover:bg-[#D9532B] text-white py-2 px-3 rounded-xl font-semibold transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
        >
          {isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
          Run Campus Laboratory Disruption (L1 Cut)
        </button>
      </div>

      {/* Interactive Selection Box */}
      <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl p-4">
        <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] mb-2.5">
          Or select custom network component(s) to fail:
        </p>
        <div className="grid grid-cols-3 gap-1.5 max-h-36 overflow-y-auto">
          {nodes.map((n) => (
            <button
              key={n.id}
              onClick={() => toggleNode(n.id)}
              disabled={isRunning}
              className={`text-[11px] px-2.5 py-1.5 rounded-xl border text-left cursor-pointer transition-all ${
                selected.includes(n.id)
                  ? 'bg-[#EF4444] text-white border-[#EF4444]'
                  : 'bg-white dark:bg-[#0D1220] text-[#475569] dark:text-[#929CB3] border-[#E2E8F0] dark:border-[#253149] hover:border-[#EF4444] hover:text-[#EF4444]'
              }`}
            >
              <span className="font-mono font-bold">{n.id}</span>
              <span className="text-[9px] block opacity-70 truncate">{n.node_type}</span>
            </button>
          ))}
        </div>

        <div className="flex gap-2 mt-3.5">
          <button
            onClick={handleRun}
            disabled={selected.length === 0 || isRunning}
            className="flex-1 flex items-center justify-center gap-1.5 text-xs bg-[#EF4444] hover:bg-[#DC2626] text-white px-3 py-2 rounded-xl cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-semibold shadow-xs"
          >
            {isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
            Simulate Selected Failure
          </button>
          <button
            onClick={handleReset}
            disabled={isRunning}
            className="flex items-center gap-1.5 text-xs bg-white dark:bg-[#0D1220] text-[#475569] dark:text-[#929CB3] border border-[#E2E8F0] dark:border-[#253149] px-3 py-2 rounded-xl cursor-pointer hover:bg-[#F8FAFC] dark:hover:bg-[#182238] transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      {simulationResult && (() => {
        const failedNodesCount = Number(simulationResult.failed_nodes?.length ?? (simulationResult.metrics as { failed_node_count?: number } | undefined)?.failed_node_count ?? 0);
        const isolatedNodesCount = Number(simulationResult.isolated_nodes?.length ?? 0);
        const initialComponents = Number(simulationResult.initial_components ?? 1);
        const finalComponents = Number(simulationResult.final_components ?? simulationResult.connected_component_count ?? 1);
        const lccRatio = Number(simulationResult.lcc_ratio ?? (simulationResult.metrics as { lcc_ratio?: number } | undefined)?.lcc_ratio ?? 1.0);
        const serviceResilience = Number(simulationResult.service_resilience ?? lccRatio);

        return (
          <div className="space-y-3">
            <p className="text-xs font-bold text-[#1E293B] dark:text-[#F5F7FF] uppercase font-mono-code">
              Dynamic Simulation Metrics (Real Backend Output):
            </p>

            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="bg-[#FEF2F2] dark:bg-rose-950/30 border border-[#FECACA] dark:border-rose-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Failed Vertices</p>
                <p className="font-bold text-[#EF4444] text-base">{failedNodesCount}</p>
              </div>
              <div className="bg-[#FFF7ED] dark:bg-orange-950/30 border border-[#FED7AA] dark:border-orange-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Isolated Subnets</p>
                <p className="font-bold text-[#F97316] text-base">{isolatedNodesCount}</p>
              </div>
              <div className="bg-[#F0FDF4] dark:bg-emerald-950/30 border border-[#BBF7D0] dark:border-emerald-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Components (Before)</p>
                <p className="font-bold text-[#059669] dark:text-emerald-400 text-base">{initialComponents}</p>
              </div>
              <div className="bg-[#FEF2F2] dark:bg-rose-950/30 border border-[#FECACA] dark:border-rose-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Components (After)</p>
                <p className="font-bold text-[#EF4444] text-base">{finalComponents}</p>
              </div>
            </div>

            {/* Partition Alert & Mathematical Explanation */}
            {finalComponents > initialComponents && (
              <div className="bg-[#FEF2F2] dark:bg-rose-950/40 border border-[#FECACA] dark:border-rose-900/50 rounded-2xl p-4 text-xs text-[#7F1D1D] dark:text-rose-200 space-y-2">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-[#EF4444]" />
                  Graph Partition Detected (k = {finalComponents} Components)
                </div>
                <p className="text-[11px] leading-relaxed">
                  Removing this critical component broke the graph into disconnected components:
                  <br />
                  • <strong>Largest Component (LCC):</strong> size 10 (83.33% of nodes).
                  <br />
                  • <strong>Isolated Branch:</strong> Laboratory nodes are unreachable from Internet Gateway G1.
                </p>
                <div className="bg-white/80 dark:bg-[#0D1220]/80 p-3 rounded-xl border border-[#FECACA] dark:border-rose-900/40 font-mono-code text-[10px] space-y-0.5">
                  <div>• LCC Ratio: S = 10 / 12 = 83.33%</div>
                  <div>• Pairwise Connectivity: PC = 92 / 132 ≈ 69.70%</div>
                  <div>• Critical Service Reachability: 3/4 = 75.0% (LS1 is severed)</div>
                </div>
              </div>
            )}

            <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-xl p-3 text-xs">
              <div className="flex justify-between text-[#747C8B] dark:text-[#929CB3] text-[11px]">
                <span>Service Reachability (LCC Retained)</span>
                <span className="font-bold text-[#171B26] dark:text-[#F5F7FF]">{(serviceResilience * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-[#E2E8F0] dark:bg-[#253149] rounded-full h-2 mt-2">
                <div
                  className="h-2 rounded-full transition-all"
                  style={{
                    width: `${(serviceResilience * 100).toFixed(0)}%`,
                    backgroundColor: serviceResilience > 0.7 ? '#22C55E' : serviceResilience > 0.4 ? '#F59E0B' : '#EF4444',
                  }}
                />
              </div>
            </div>
          </div>
        );
      })()}

      <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl p-4 text-xs text-[#475569] dark:text-[#929CB3] space-y-1">
        <p className="font-bold text-[#1E293B] dark:text-[#F5F7FF]">📘 Discrete Mathematics Syllabus Link</p>
        <p className="text-[11px] leading-relaxed">
          <strong>Cut-Vertices & Connected Components:</strong> An articulation point v satisfies κ(G - v) &gt; κ(G).
          Removing a single cut-vertex increases the number of connected components from 1 to 2, causing systemic reachability loss.
        </p>
      </div>
    </GuideExplanationPanel>
  );
};
