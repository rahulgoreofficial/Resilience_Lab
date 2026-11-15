/**
 * Chapter 5 — Cascading Failures
 * Features the Controlled 5-Node Cascading Overload Demonstration (Requirement 6)
 */

import React, { useState } from 'react';
import { Loader, PlayCircle, RotateCcw, AlertOctagon, Info } from 'lucide-react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData } from '../../types/network';
import type { SimulationResults } from '../../types/simulation';

interface Props {
  nodes: CytoscapeNodeData[];
  onRunCascading: (nodeId: string, threshold: number, maxRounds: number) => Promise<void>;
  onReset: () => void;
  simulationResult: SimulationResults | null;
  isRunning: boolean;
}

export const Chapter5: React.FC<Props> = ({
  nodes, onRunCascading, onReset, simulationResult, isRunning,
}) => {
  const [selectedNode, setSelectedNode] = useState('');
  const [threshold, setThreshold] = useState(1.0);
  const [maxRounds] = useState(6);

  const handleRun = async () => {
    if (!selectedNode) return;
    await onRunCascading(selectedNode, threshold, maxRounds);
  };

  const handleRunControlledCascade = async () => {
    // If PR1 exists, target PR1, else first router
    const target = nodes.find(n => n.id === 'PR1' || n.id === 'R1')?.id || nodes[0]?.id;
    if (target) {
      setSelectedNode(target);
      await onRunCascading(target, 1.0, 5);
    }
  };

  const events = simulationResult?.events ?? [];

  return (
    <GuideExplanationPanel
      chapterId={5}
      title="Cascading Failures"
      subtitle="How one broken device triggers dynamic load redistribution and secondary failures."
    >
      <p>
        In production networks, when a primary router breaks, traffic does not disappear — it <strong>reroutes</strong> along alternative shortest paths.
        If backup devices lack sufficient capacity, the redirected load triggers <strong>cascading failure propagation</strong>.
      </p>

      {/* Controlled Cascading Scenario Banner */}
      <div className="bg-[#FAF5FF] dark:bg-purple-950/30 border-2 border-[#9333EA]/40 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold font-mono-code uppercase text-[#9333EA] dark:text-[#9B7BFF] flex items-center gap-1.5">
            <AlertOctagon className="w-3.5 h-3.5" />
            Controlled Cascading Scenario
          </span>
          <span className="text-[10px] bg-[#9333EA] text-white px-2 py-0.5 rounded-full font-bold">
            SECTION 6
          </span>
        </div>

        <div className="text-xs text-[#171B26] dark:text-[#F5F7FF] font-semibold">
          Primary Router (PR1) Failure & Backup Router (BR1) Overload
        </div>

        <div className="bg-white/80 dark:bg-[#0D1220]/80 p-3 rounded-xl border border-[#E9D5FF] dark:border-purple-900/40 text-[11px] text-[#581C87] dark:text-purple-200 space-y-1">
          <div>• <strong>Primary Router PR1:</strong> Capacity 500, Background Load 100</div>
          <div>• <strong>Backup Router BR1:</strong> Capacity 350, Background Load 100</div>
          <div>• <strong>Client Demand:</strong> 300 Mbps from Client Workstation CL1 to Server SRV_APP</div>
          <div className="text-[10px] text-[#7E22CE] dark:text-[#9B7BFF] italic pt-1 border-t border-[#F3E8FF] dark:border-purple-900/40">
            When PR1 fails, 300 Mbps traffic shifts onto BR1 → BR1 Total Load = 100 + 300 = 400 Mbps &gt; 350 Mbps capacity! BR1 fails in Round 2.
          </div>
        </div>

        <button
          onClick={handleRunControlledCascade}
          disabled={isRunning}
          className="w-full flex items-center justify-center gap-1.5 text-xs bg-[#9333EA] hover:bg-[#7E22CE] text-white py-2 px-3 rounded-xl font-semibold transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
        >
          {isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
          Run Controlled PR1 Overload Cascade
        </button>
      </div>

      {/* Manual Configuration */}
      <div className="space-y-3 bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl p-4">
        <div>
          <label className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] block mb-1.5">Or Trigger Cascade from Selected Device:</label>
          <select
            value={selectedNode}
            onChange={(e) => setSelectedNode(e.target.value)}
            disabled={isRunning}
            className="w-full text-xs border border-[#E2E8F0] dark:border-[#253149] rounded-xl px-3 py-2 bg-white dark:bg-[#0D1220] text-[#171B26] dark:text-[#F5F7FF] focus:outline-none focus:border-purple-500 font-mono-code"
          >
            <option value="">— Select a device —</option>
            {nodes.map((n) => (
              <option key={n.id} value={n.id}>{n.id} ({n.node_type})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] block mb-1">
            Overload Capacity Threshold: <span className="text-[#F2653A]">{(threshold * 100).toFixed(0)}%</span>
          </label>
          <input
            type="range" min={0.5} max={1.5} step={0.1}
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            disabled={isRunning}
            className="w-full accent-purple-600"
          />
          <p className="text-[10px] text-[#94A3B8] dark:text-[#69758E]">A router fails when (background_load + routed_traffic) &gt; capacity × threshold.</p>
        </div>

        <div className="flex gap-2 pt-1">
          <button
            onClick={handleRun}
            disabled={!selectedNode || isRunning}
            className="flex-1 flex items-center justify-center gap-1.5 text-xs bg-[#9333EA] hover:bg-[#7E22CE] text-white px-3 py-2 rounded-xl cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-semibold shadow-xs"
          >
            {isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
            Execute Dynamic Cascade
          </button>
          <button
            onClick={() => { setSelectedNode(''); onReset(); }}
            disabled={isRunning}
            className="flex items-center gap-1.5 text-xs bg-white dark:bg-[#0D1220] text-[#475569] dark:text-[#929CB3] border border-[#E2E8F0] dark:border-[#253149] px-3 py-2 rounded-xl cursor-pointer hover:bg-[#F8FAFC] dark:hover:bg-[#182238] transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Reset
          </button>
        </div>
      </div>

      {simulationResult && (() => {
        const cascadeRounds = simulationResult.cascade_rounds ?? (simulationResult.metrics as { total_cascading_rounds?: number } | undefined)?.total_cascading_rounds ?? 0;
        const timeline = (simulationResult as { timeline?: Array<{ round: number; state_description?: string; newly_failed_nodes?: string[]; traffic_served?: number; traffic_unserved?: number }> }).timeline ?? [];

        return (
          <div className="space-y-3">
            <p className="text-xs font-bold text-[#1E293B] dark:text-[#F5F7FF] uppercase font-mono-code">
              Iterative Cascade Timeline (Real Backend Results):
            </p>
            <div className="grid grid-cols-3 gap-2 text-[11px]">
              <div className="bg-[#FEF2F2] dark:bg-rose-950/30 border border-[#FECACA] dark:border-rose-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Rounds</p>
                <p className="font-bold text-[#EF4444] text-base">{cascadeRounds}</p>
              </div>
              <div className="bg-[#FEF2F2] dark:bg-rose-950/30 border border-[#FECACA] dark:border-rose-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Total Failed</p>
                <p className="font-bold text-[#EF4444] text-base">{simulationResult.failed_nodes?.length ?? 0}</p>
              </div>
              <div className="bg-[#F0FDF4] dark:bg-emerald-950/30 border border-[#BBF7D0] dark:border-emerald-900/40 rounded-xl p-3 text-center">
                <p className="text-[#747C8B] dark:text-[#929CB3]">Survived</p>
                <p className="font-bold text-[#059669] dark:text-emerald-400 text-base">
                  {nodes.length - (simulationResult.failed_nodes?.length ?? 0)}
                </p>
              </div>
            </div>

            {timeline.length > 0 ? (
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {timeline.map((item, i) => (
                  <div key={i} className="text-[11px] bg-[#FFF1F2] dark:bg-rose-950/40 border-l-3 border-[#EF4444] px-3 py-2 rounded-r-xl">
                    <div className="font-mono text-[#9F1239] dark:text-rose-300 font-bold">
                      Round {item.round}: {item.state_description || 'Cascade Propagation'}
                    </div>
                    {item.newly_failed_nodes && item.newly_failed_nodes.length > 0 && (
                      <div className="text-[#475569] dark:text-[#929CB3] text-[10px] mt-0.5">
                        Overloaded & Failed: <span className="font-mono font-bold text-[#EF4444]">[{item.newly_failed_nodes.join(', ')}]</span>
                      </div>
                    )}
                    {item.traffic_unserved !== undefined && item.traffic_unserved > 0 && (
                      <div className="text-[#B91C1C] dark:text-rose-400 text-[10px] font-semibold">
                        Traffic Dropped / Unserved: {item.traffic_unserved} Mbps
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : events.length > 0 ? (
              <div className="space-y-1 max-h-36 overflow-y-auto">
                {events.map((ev, i) => (
                  <div key={i} className="text-[11px] bg-[#FFF1F2] dark:bg-rose-950/40 border-l-2 border-[#EF4444] px-3 py-1.5 rounded-r-xl">
                    <span className="font-mono text-[#9F1239] dark:text-rose-300 font-bold">
                      {ev.round !== undefined ? `Round ${ev.round}: ` : ''}{ev.event}
                    </span>
                  </div>
                ))}
              </div>
            ) : null}
          </div>
        );
      })()}

      {/* Traffic Model Simplifying Assumptions */}
      <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl p-4 text-xs text-[#475569] dark:text-[#929CB3] space-y-1.5">
        <div className="font-bold text-[#1E293B] dark:text-[#F5F7FF] flex items-center gap-1.5 uppercase font-mono-code text-[11px]">
          <Info className="w-3.5 h-3.5 text-[#3B82F6]" />
          Traffic Model Simplifying Assumptions
        </div>
        <ul className="list-disc pl-4 space-y-0.5 text-[11px] leading-relaxed">
          <li><strong>Single Shortest-Path Routing:</strong> Traffic follows Dijkstra shortest path without multi-path flow splitting (ECMP).</li>
          <li><strong>Instantaneous Reallocation:</strong> Packets divert immediately upon link or node disruption without re-convergence delay.</li>
          <li><strong>Discrete Threshold:</strong> A router trips into permanent failure if aggregate traffic exceeds configured capacity.</li>
        </ul>
      </div>
    </GuideExplanationPanel>
  );
};
