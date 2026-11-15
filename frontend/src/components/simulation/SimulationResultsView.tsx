import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Activity, 
  Layers, 
  Copy 
} from 'lucide-react';
import type { SimulationResults, SimulationEvent } from '../../types/simulation';
import { Button } from '../common/Button';

export interface SimulationResultsViewProps {
  results: SimulationResults | null;
  events?: SimulationEvent[];
  onSelectNode?: (nodeId: string) => void;
  isLoading?: boolean;
}

export const SimulationResultsView: React.FC<SimulationResultsViewProps> = ({
  results,
  events = [],
  onSelectNode,
  isLoading = false
}) => {
  const [activeTab, setActiveTab] = useState<'summary' | 'events' | 'json'>('summary');
  const [copied, setCopied] = useState(false);

  if (isLoading) {
    return (
      <div className="p-12 text-center bg-white/95 dark:bg-[#0D1220]/95 border border-slate-200/90 dark:border-[#253149] rounded-3xl shadow-sm backdrop-blur-md text-[#171923] dark:text-[#F5F7FF]">
        <Activity className="w-10 h-10 text-[#4F8CFF] animate-spin mx-auto mb-4" />
        <h4 className="text-base font-bold text-[#171923] dark:text-[#F5F7FF]">Solving Graph Disruption Equations...</h4>
        <p className="text-xs text-[#737B8C] dark:text-[#929CB3] mt-1 max-w-sm mx-auto">Evaluating connected components, reachability matrices, and spectral impact.</p>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="p-12 text-center bg-white/90 dark:bg-[#0D1220]/90 border border-slate-200/80 dark:border-[#253149] rounded-3xl shadow-xs text-[#171923] dark:text-[#F5F7FF]">
        <Layers className="w-10 h-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
        <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Awaiting Simulation Execution</h4>
        <p className="text-xs text-[#737B8C] dark:text-[#929CB3] mt-1 max-w-sm mx-auto">Select failure parameters in the configuration panel and click "Execute Simulation" to generate outcomes.</p>
      </div>
    );
  }

  const lccRatio = results.lcc_ratio ?? 1.0;
  const pairwiseRatio = results.pairwise_connectivity_ratio ?? 1.0;
  const initialComp = results.initial_components ?? 1;
  const finalComp = results.final_components ?? 1;
  const failedNodes = results.failed_nodes || [];
  const isolatedNodes = results.isolated_nodes || [];
  const unreachableNodes = (Array.isArray(results.unreachable_nodes) ? results.unreachable_nodes : []) as string[];

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(results, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-3xl shadow-sm overflow-hidden flex flex-col text-[#171923] dark:text-[#F5F7FF] transition-colors">
      {/* Header */}
      <div className="px-6 py-5 border-b border-slate-100 dark:border-[#253149] flex flex-wrap items-center justify-between gap-3 bg-slate-50/60 dark:bg-[#121A2B]/70">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-[#20D6A0] border border-emerald-200/80 dark:border-emerald-800/60">
            <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-[#20D6A0]" />
          </div>
          <div>
            <h3 className="text-base font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
              Simulation Outcomes & Resilience Impact
            </h3>
            {results.simulation_id && (
              <span className="text-[11px] text-slate-400 dark:text-[#69758E] font-mono-code">
                UUID: {results.simulation_id}
              </span>
            )}
          </div>
        </div>

        {/* Tab switchers */}
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-[#121A2B] p-1 rounded-xl border border-slate-200 dark:border-[#253149]">
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-3.5 py-1.5 text-xs rounded-lg font-semibold cursor-pointer transition-all ${
              activeTab === 'summary' 
                ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs' 
                : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
            }`}
          >
            Metrics Summary
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`px-3.5 py-1.5 text-xs rounded-lg font-semibold cursor-pointer transition-all ${
              activeTab === 'events' 
                ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs' 
                : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
            }`}
          >
            Propagation Timeline
          </button>
          <button
            onClick={() => setActiveTab('json')}
            className={`px-3.5 py-1.5 text-xs rounded-lg font-semibold cursor-pointer transition-all ${
              activeTab === 'json' 
                ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs' 
                : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
            }`}
          >
            Raw JSON
          </button>
        </div>
      </div>

      {/* Tab: Summary */}
      {activeTab === 'summary' && (
        <div className="p-6 space-y-6">
          {/* Top KPI Cards (Large numerical typography) */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">LCC Retention</span>
              <div className={`text-3xl font-extrabold font-mono-code mt-1 ${lccRatio < 0.6 ? 'text-rose-600 dark:text-[#FF5364]' : 'text-emerald-600 dark:text-[#20D6A0]'}`}>
                {(lccRatio * 100).toFixed(1)}%
              </div>
              <span className="text-[11px] text-slate-400 dark:text-[#69758E] mt-1 block">Surviving giant cluster</span>
            </div>

            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Pairwise Reachability</span>
              <div className={`text-3xl font-extrabold font-mono-code mt-1 ${pairwiseRatio < 0.6 ? 'text-rose-600 dark:text-[#FF5364]' : 'text-emerald-600 dark:text-[#20D6A0]'}`}>
                {(pairwiseRatio * 100).toFixed(1)}%
              </div>
              <span className="text-[11px] text-slate-400 dark:text-[#69758E] mt-1 block">Connected vertex pairs</span>
            </div>

            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Partitioned Islands</span>
              <div className="text-3xl font-extrabold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-1">
                {initialComp} &rarr; <span className={finalComp > initialComp ? 'text-[#FF784F]' : 'text-slate-900 dark:text-[#F5F7FF]'}>{finalComp}</span>
              </div>
              <span className="text-[11px] text-slate-400 dark:text-[#69758E] mt-1 block">Disconnected subgraphs</span>
            </div>

            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Offline Components</span>
              <div className="text-3xl font-extrabold font-mono-code text-rose-600 dark:text-[#FF5364] mt-1">
                {failedNodes.length} nodes
              </div>
              <span className="text-[11px] text-slate-400 dark:text-[#69758E] mt-1 block">{isolatedNodes.length} isolated · {unreachableNodes.length} severed</span>
            </div>
          </div>

          {/* Detailed Lists Presentation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-1">
            <div className="p-5 bg-slate-50/80 dark:bg-[#121A2B]/60 border border-slate-200/80 dark:border-[#253149] rounded-2xl space-y-3">
              <h5 className="text-xs font-bold text-slate-800 dark:text-[#F5F7FF] font-mono-code uppercase tracking-wider flex items-center justify-between">
                <span>Directly Inactivated Nodes</span>
                <span className="text-rose-600 dark:text-[#FF5364] font-semibold">{failedNodes.length}</span>
              </h5>
              {failedNodes.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {failedNodes.map((id) => (
                    <button
                      key={id}
                      onClick={() => onSelectNode?.(id)}
                      className="px-3 py-1 bg-white dark:bg-[#182238] border border-rose-300 dark:border-rose-500/40 text-rose-700 dark:text-[#FF5364] rounded-xl font-mono-code text-xs font-bold hover:bg-rose-50 dark:hover:bg-rose-950/40 cursor-pointer shadow-2xs"
                    >
                      {id}
                    </button>
                  ))}
                </div>
              ) : (
                <span className="text-slate-400 dark:text-[#69758E] text-xs italic">No directly failed nodes</span>
              )}
            </div>

            <div className="p-5 bg-slate-50/80 dark:bg-[#121A2B]/60 border border-slate-200/80 dark:border-[#253149] rounded-2xl space-y-3">
              <h5 className="text-xs font-bold text-slate-800 dark:text-[#F5F7FF] font-mono-code uppercase tracking-wider flex items-center justify-between">
                <span>Severed / Isolated Services</span>
                <span className="text-amber-600 dark:text-[#F6BD60] font-semibold">{isolatedNodes.length}</span>
              </h5>
              {isolatedNodes.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {isolatedNodes.map((id) => (
                    <button
                      key={id}
                      onClick={() => onSelectNode?.(id)}
                      className="px-3 py-1 bg-white dark:bg-[#182238] border border-amber-300 dark:border-amber-500/40 text-amber-800 dark:text-[#F6BD60] rounded-xl font-mono-code text-xs font-bold hover:bg-amber-50 dark:hover:bg-amber-950/40 cursor-pointer shadow-2xs"
                    >
                      {id}
                    </button>
                  ))}
                </div>
              ) : (
                <span className="text-slate-400 dark:text-[#69758E] text-xs italic">Zero components isolated</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab: Events Timeline */}
      {activeTab === 'events' && (
        <div className="p-6">
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {(events.length > 0 ? events : (results.events || [])).map((ev: any, i: number) => {
              const seq = ev.sequence_number ?? ev.round ?? (i + 1);
              const eventName = String(ev.event_type ?? ev.event ?? 'Topology Event');
              const timeStr = ev.created_at ? new Date(String(ev.created_at)).toLocaleTimeString() : `Round ${seq}`;
              return (
                <div key={i} className="p-3.5 bg-slate-50 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl flex items-center justify-between text-xs font-mono-code text-[#171923] dark:text-[#F5F7FF]">
                  <div className="flex items-center gap-3">
                    <span className="w-6 h-6 rounded-lg bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-[#9B7BFF] flex items-center justify-center font-bold text-[11px] border border-indigo-200/50 dark:border-indigo-800/40">
                      {seq}
                    </span>
                    <span className="font-semibold text-slate-900 dark:text-[#F5F7FF]">{eventName}</span>
                  </div>
                  <span className="text-[11px] text-slate-400 dark:text-[#69758E]">
                    {timeStr}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab: Raw JSON */}
      {activeTab === 'json' && (
        <div className="p-6 space-y-3">
          <div className="flex justify-end">
            <Button size="sm" variant="outline" icon={<Copy className="w-3.5 h-3.5" />} onClick={handleCopyJson}>
              {copied ? 'Copied!' : 'Copy JSON'}
            </Button>
          </div>
          <pre className="p-4 bg-slate-950 text-cyan-400 border border-slate-800 rounded-2xl overflow-x-auto text-[11px] font-mono-code max-h-96">
            {JSON.stringify(results, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
