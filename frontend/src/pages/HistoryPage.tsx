import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  RotateCcw, 
  ChevronRight, 
  Play, 
  X,
  Copy,
  History
} from 'lucide-react';
import type { Network } from '../types/network';
import type { SimulationRecord, SimulationEvent } from '../types/simulation';
import { listSimulations, getSimulationEvents } from '../services/simulationService';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';

export interface HistoryPageProps {
  selectedNetwork: Network | null;
  onNavigateToSimulation: () => void;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({
  selectedNetwork,
  onNavigateToSimulation
}) => {
  const [simulations, setSimulations] = useState<SimulationRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<SimulationRecord | null>(null);
  const [selectedEvents, setSelectedEvents] = useState<SimulationEvent[]>([]);
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingEvents, setIsLoadingEvents] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const res = await listSimulations(selectedNetwork?.id, 0, 100);
      setSimulations(res.items);
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [selectedNetwork?.id]);

  const handleCopyId = (id: string) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const handleSelectRecord = async (record: SimulationRecord) => {
    setSelectedRecord(record);
    setIsLoadingEvents(true);
    try {
      const events = await getSimulationEvents(record.id);
      setSelectedEvents(events);
    } catch {
      setSelectedEvents([]);
    } finally {
      setIsLoadingEvents(false);
    }
  };

  const filteredSimulations = simulations.filter((sim) => {
    const matchesType = typeFilter === 'all' || sim.simulation_type === typeFilter;
    const matchesSearch =
      searchQuery === '' ||
      sim.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sim.simulation_type.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  return (
    <div className="space-y-6 pb-10">
      {/* Top Banner */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-6 shadow-xs flex flex-wrap items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl font-extrabold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Simulation Audit Log & History</h2>
            <Badge variant="brand">Database Persistence</Badge>
          </div>
          <p className="text-xs sm:text-sm text-[#737B8C] dark:text-[#929CB3] mt-1">
            Permanent records of deterministic component outages, adversarial attacks and cascading overload propagations.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            icon={<RotateCcw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={loadHistory}
            disabled={isLoading}
          >
            Refresh Log
          </Button>
          <Button
            variant="brand"
            size="sm"
            icon={<Play className="w-3.5 h-3.5 text-white" />}
            onClick={onNavigateToSimulation}
          >
            New Simulation
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-4 shadow-xs flex flex-wrap items-center justify-between gap-4 text-xs transition-colors">
        <div className="flex items-center gap-2 min-w-[260px] flex-1">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search by simulation ID or target..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-800 dark:text-[#F5F7FF] focus:outline-none focus:border-indigo-500 font-mono-code transition-colors"
          />
        </div>

        <div className="flex items-center gap-2.5">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-500 dark:text-[#929CB3] font-mono-code font-semibold uppercase text-[11px]">Mode:</span>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3 py-1.5 text-xs text-slate-800 dark:text-[#F5F7FF] focus:outline-none cursor-pointer font-mono-code font-medium"
          >
            <option value="all">All Modes ({simulations.length})</option>
            <option value="node_failure">Node Failure</option>
            <option value="edge_failure">Edge Failure</option>
            <option value="multiple_failure">Multiple Failure</option>
            <option value="random">Random Failure</option>
            <option value="targeted">Targeted Adversarial</option>
            <option value="cascading">Cascading Overload</option>
          </select>
        </div>
      </div>

      {/* Main Runs Table */}
      <Card
        header={
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-900 dark:text-[#F5F7FF] tracking-tight">Recorded Execution History</h3>
            <span className="text-xs font-mono-code text-slate-400 dark:text-[#69758E]">{filteredSimulations.length} runs cataloged</span>
          </div>
        }
      >
        {filteredSimulations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono-code">
              <thead className="bg-slate-50/80 dark:bg-[#121A2B]/80 border-b border-slate-100 dark:border-[#253149] text-slate-500 dark:text-[#929CB3] uppercase text-[11px] font-semibold">
                <tr>
                  <th className="px-5 py-3.5">Simulation Identifier</th>
                  <th className="px-5 py-3.5">Strategy / Mode</th>
                  <th className="px-5 py-3.5">Status</th>
                  <th className="px-5 py-3.5">Giant Comp (LCC)</th>
                  <th className="px-5 py-3.5">Execution Time</th>
                  <th className="px-5 py-3.5 text-right font-sans">Inspect</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-[#253149]">
                {filteredSimulations.map((sim) => (
                  <tr key={sim.id} className="hover:bg-slate-50/80 dark:hover:bg-[#182238]/60 transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 dark:text-[#F5F7FF]">{sim.id.slice(0, 8)}...</span>
                        <button
                          onClick={() => handleCopyId(sim.id)}
                          className="text-slate-400 hover:text-slate-700 dark:hover:text-[#F5F7FF] cursor-pointer"
                          title="Copy UUID"
                        >
                          <Copy className="w-3 h-3" />
                        </button>
                        {copiedId === sim.id && <span className="text-[10px] text-emerald-600 dark:text-[#20D6A0] font-sans">Copied!</span>}
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <Badge variant="cyan" size="sm">{sim.simulation_type}</Badge>
                    </td>
                    <td className="px-5 py-4">
                      <Badge variant={sim.status === 'completed' ? 'healthy' : sim.status === 'failed' ? 'failed' : 'warning'} size="sm">
                        {sim.status}
                      </Badge>
                    </td>
                    <td className="px-5 py-4 font-bold text-slate-900 dark:text-[#F5F7FF]">
                      {sim.results?.lcc_ratio !== undefined ? `${(sim.results.lcc_ratio * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="px-5 py-4 text-slate-500 dark:text-[#929CB3] font-sans">
                      {new Date(sim.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-4 text-right font-sans">
                      <Button
                        size="sm"
                        variant="secondary"
                        icon={<ChevronRight className="w-3.5 h-3.5 text-slate-600 dark:text-slate-300" />}
                        onClick={() => handleSelectRecord(sim)}
                      >
                        Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-sm text-[#737B8C] dark:text-[#929CB3]">
            No simulation runs matching filter criteria.
          </div>
        )}
      </Card>

      {/* Selected Run Modal / Slide-over Drawer */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-2xl bg-white dark:bg-[#0D1220] rounded-3xl shadow-2xl border border-slate-200 dark:border-[#253149] overflow-hidden text-[#171923] dark:text-[#F5F7FF]">
            <div className="px-6 py-5 border-b border-slate-100 dark:border-[#253149] flex items-center justify-between bg-slate-50/60 dark:bg-[#121A2B]/70">
              <div className="flex items-center gap-2.5">
                <History className="w-5 h-5 text-indigo-600 dark:text-[#9B7BFF]" />
                <h3 className="text-base font-bold text-slate-900 dark:text-[#F5F7FF]">Simulation Run Details</h3>
              </div>
              <button
                onClick={() => setSelectedRecord(null)}
                className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-[#F5F7FF] hover:bg-slate-200/60 dark:hover:bg-[#182238] rounded-full cursor-pointer transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
              <div className="p-4 bg-slate-50 dark:bg-[#121A2B]/80 rounded-2xl border border-slate-200/90 dark:border-[#253149] font-mono-code text-xs space-y-2">
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-[#929CB3]">UUID:</span>
                  <span className="font-bold text-slate-900 dark:text-[#F5F7FF]">{selectedRecord.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-[#929CB3]">Mode:</span>
                  <span className="font-bold text-indigo-600 dark:text-[#9B7BFF]">{selectedRecord.simulation_type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 dark:text-[#929CB3]">Timestamp:</span>
                  <span className="text-slate-800 dark:text-slate-200">{new Date(selectedRecord.created_at).toLocaleString()}</span>
                </div>
              </div>

              {selectedRecord.results && (
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-slate-50 dark:bg-[#121A2B]/80 rounded-xl border border-slate-200 dark:border-[#253149] text-xs font-mono-code">
                    <span className="text-slate-500 dark:text-[#929CB3] uppercase">LCC Retention:</span>
                    <div className="text-xl font-bold text-emerald-600 dark:text-[#20D6A0] mt-0.5">
                      {((selectedRecord.results.lcc_ratio || 1) * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-[#121A2B]/80 rounded-xl border border-slate-200 dark:border-[#253149] text-xs font-mono-code">
                    <span className="text-slate-500 dark:text-[#929CB3] uppercase">Pairwise Ratio:</span>
                    <div className="text-xl font-bold text-cyan-600 dark:text-cyan-400 mt-0.5">
                      {((selectedRecord.results.pairwise_connectivity_ratio || 1) * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              )}

              {/* Events Breakdown */}
              <div className="space-y-2">
                <span className="text-xs font-bold text-slate-700 dark:text-[#F5F7FF] font-mono-code uppercase">Events Timeline</span>
                <div className="space-y-1.5 max-h-48 overflow-y-auto p-2 bg-slate-50 dark:bg-[#121A2B]/60 border border-slate-200 dark:border-[#253149] rounded-xl">
                  {isLoadingEvents ? (
                    <span className="text-slate-400 dark:text-[#69758E] text-xs italic p-2 block">Loading event trace...</span>
                  ) : selectedEvents.length > 0 ? (
                    selectedEvents.map((ev, idx) => (
                      <div key={idx} className="p-2 bg-white dark:bg-[#182238] rounded-lg border border-slate-200/80 dark:border-[#253149] text-xs font-mono-code flex justify-between text-slate-800 dark:text-[#F5F7FF]">
                        <span className="font-semibold text-slate-800 dark:text-[#F5F7FF]">{ev.event_type}</span>
                        <span className="text-slate-400 dark:text-[#69758E]">Step {ev.sequence_number ?? idx + 1}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-400 dark:text-[#69758E] text-xs italic p-2 block">No event trace recorded for this run.</span>
                  )}
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-slate-100 dark:border-[#253149] bg-slate-50/80 dark:bg-[#121A2B]/80 flex justify-end">
              <Button size="sm" variant="secondary" onClick={() => setSelectedRecord(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
