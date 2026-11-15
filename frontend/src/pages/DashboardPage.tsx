import React from 'react';
import { 
  Network as NetworkIcon, 
  Activity, 
  ShieldAlert, 
  ArrowRight, 
  Play, 
  GitFork, 
  Plus, 
  Upload, 
  FileText, 
  CheckCircle2, 
  Clock, 
  Sparkles 
} from 'lucide-react';
import type { Network } from '../types/network';
import type { ConnectivityAnalysis } from '../types/analytics';
import type { SimulationRecord } from '../types/simulation';
import { MetricItem } from '../components/common/MetricItem';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { NetworkMeshIllustration } from '../components/common/NetworkMeshIllustration';

export interface DashboardPageProps {
  selectedNetwork: Network | null;
  analysis: ConnectivityAnalysis | null;
  recentSimulations: SimulationRecord[];
  onNavigateToTopology: () => void;
  onNavigateToSimulation: () => void;
  onNavigateToAnalytics: () => void;
  onCreateNetworkClick: () => void;
  onImportNetworkClick?: () => void;
  onSelectNodeInTopology?: (nodeId: string) => void;
  onOpenReport?: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  selectedNetwork,
  analysis,
  recentSimulations,
  onNavigateToTopology,
  onNavigateToSimulation,
  onNavigateToAnalytics,
  onCreateNetworkClick,
  onImportNetworkClick,
  onSelectNodeInTopology,
  onOpenReport
}) => {
  if (!selectedNetwork) {
    return (
      <div className="p-12 text-center bg-white/80 dark:bg-[#0D1220]/80 border border-slate-200/80 dark:border-[#253149] rounded-3xl shadow-sm backdrop-blur-md">
        <NetworkIcon className="w-12 h-12 text-slate-400 mx-auto mb-4" />
        <h3 className="text-lg font-bold text-[#171923] dark:text-[#F5F7FF]">No Active Infrastructure Selected</h3>
        <p className="text-sm text-[#737B8C] dark:text-[#929CB3] mt-1 max-w-md mx-auto">
          Please select an existing network topology from the top navigation or create a new graph to initiate resilience calculations.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button variant="brand" onClick={onCreateNetworkClick} icon={<Plus className="w-4 h-4" />}>
            Create Network
          </Button>
          {onImportNetworkClick && (
            <Button variant="outline" onClick={onImportNetworkClick} icon={<Upload className="w-4 h-4" />}>
              Import JSON
            </Button>
          )}
        </div>
      </div>
    );
  }

  const nodeCount = analysis?.node_count ?? selectedNetwork.node_count;
  const edgeCount = analysis?.edge_count ?? selectedNetwork.edge_count;
  const componentCount = analysis?.connected_components_count ?? 1;
  const apCount = analysis?.articulation_points.length ?? 0;
  const bridgeCount = analysis?.bridges.length ?? 0;
  const lccRatio = analysis?.lcc_ratio ?? 1.0;
  const algebraicConn = analysis?.algebraic_connectivity !== undefined ? analysis.algebraic_connectivity.toFixed(4) : 'N/A';

  return (
    <div className="space-y-8 pb-10">
      {/* ─── Hero Section with Apple-Inspired Minimalism & Glowing Mesh ─── */}
      <div className="relative bg-gradient-to-br from-[#080B14] via-[#0D1220] to-[#121A2B] text-white rounded-3xl overflow-hidden border border-slate-800 dark:border-[#253149] shadow-2xl p-8 sm:p-12 lg:p-14">
        {/* Subtle Ambient Background Disc */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-[#6366F1]/20 via-[#4F8CFF]/15 to-transparent rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/4 w-80 h-80 bg-gradient-to-tr from-[#22D3EE]/10 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-800/80 dark:bg-[#182238] border border-slate-700/80 dark:border-[#253149] text-cyan-400 text-xs font-mono-code uppercase tracking-wider backdrop-blur-md">
              <span className="w-2 h-2 rounded-full bg-[#22D3EE] animate-pulse" />
              <span>Infrastructure Intelligence Platform</span>
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.08] text-white">
                SEE WHAT FAILS.<br />
                <span className="text-gradient-brand">UNDERSTAND WHAT SURVIVES.</span>
              </h1>
            </div>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl font-normal">
              Model infrastructure, expose network vulnerabilities and evaluate resilience through interactive mathematical simulations.
            </p>

            <div className="pt-2 flex flex-wrap items-center gap-4">
              <Button
                variant="brand"
                size="lg"
                icon={<Play className="w-4 h-4 text-white" />}
                onClick={onNavigateToSimulation}
              >
                RUN SIMULATION
              </Button>
              <Button
                variant="dark"
                size="lg"
                icon={<NetworkIcon className="w-4 h-4 text-[#22D3EE]" />}
                onClick={onNavigateToTopology}
              >
                EXPLORE NETWORK
              </Button>
            </div>
          </div>

          {/* Right Side: Network Mesh Illustration */}
          <div className="lg:col-span-5 relative h-80 sm:h-96 w-full flex items-center justify-center">
            <NetworkMeshIllustration className="w-full h-full object-contain" />
          </div>
        </div>
      </div>

      {/* ─── Quick Actions Bar ─── */}
      <div className="bg-white/80 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-4 shadow-sm flex flex-wrap items-center justify-between gap-3 transition-colors">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#6366F1] dark:text-[#22D3EE]" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700 dark:text-[#F5F7FF] font-mono-code">Quick Operations:</span>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" variant="outline" icon={<Plus className="w-3.5 h-3.5" />} onClick={onCreateNetworkClick}>
            Create Network
          </Button>
          {onImportNetworkClick && (
            <Button size="sm" variant="outline" icon={<Upload className="w-3.5 h-3.5 text-indigo-600 dark:text-cyan-400" />} onClick={onImportNetworkClick}>
              Import Network
            </Button>
          )}
          <Button size="sm" variant="outline" icon={<NetworkIcon className="w-3.5 h-3.5 text-[#3B82F6] dark:text-cyan-400" />} onClick={onNavigateToTopology}>
            Open Topology
          </Button>
          <Button size="sm" variant="outline" icon={<Play className="w-3.5 h-3.5 text-emerald-600 dark:text-[#20D6A0]" />} onClick={onNavigateToSimulation}>
            Run Simulation
          </Button>
          {onOpenReport && (
            <Button size="sm" variant="brand" icon={<FileText className="w-3.5 h-3.5" />} onClick={onOpenReport}>
              Generate Report
            </Button>
          )}
        </div>
      </div>

      {/* ─── Single Points of Failure Alert Banner ─── */}
      {(apCount > 0 || bridgeCount > 0) && (
        <div className="p-5 bg-gradient-to-r from-orange-50/95 via-rose-50/80 to-amber-50/60 dark:from-orange-950/25 dark:via-rose-950/20 dark:to-[#0D1220] border border-orange-200/90 dark:border-orange-500/30 rounded-2xl flex items-start gap-4 shadow-sm transition-colors">
          <div className="p-2 rounded-xl bg-orange-500/15 text-[#FF784F] shrink-0 mt-0.5 border border-orange-500/20">
            <ShieldAlert className="w-5 h-5 text-[#FF784F]" />
          </div>
          <div className="flex-1 text-xs">
            <div className="font-bold text-[#FF784F] text-sm tracking-tight flex items-center gap-2">
              <span>Single Points of Failure (SPOFs) Detected in Active Topology</span>
              <Badge variant="critical" size="sm">Topological Risk</Badge>
            </div>
            <p className="text-slate-700 dark:text-slate-300 mt-1 leading-relaxed text-xs">
              Algorithmic Tarjan analysis discovered <span className="font-bold font-mono-code text-[#FF784F]">{apCount} cut-vertex node(s)</span> and{' '}
              <span className="font-bold font-mono-code text-[#FF784F]">{bridgeCount} bridge link(s)</span>. Failure of any marked component will partition the communication graph.
            </p>
            {analysis?.articulation_points && analysis.articulation_points.length > 0 && (
              <div className="flex flex-wrap items-center gap-2 mt-3">
                <span className="text-[11px] uppercase font-mono-code text-slate-500 dark:text-[#929CB3] font-semibold">Cut-Vertices:</span>
                {analysis.articulation_points.slice(0, 8).map((ap) => (
                  <button
                    key={ap}
                    onClick={() => {
                      onSelectNodeInTopology?.(ap);
                      onNavigateToTopology();
                    }}
                    className="px-2.5 py-1 bg-white dark:bg-[#121A2B] border border-orange-300/80 dark:border-orange-500/40 text-[#FF784F] rounded-lg font-mono-code text-xs font-semibold hover:bg-orange-50 dark:hover:bg-[#182238] hover:border-orange-400 transition-colors cursor-pointer shadow-2xs"
                  >
                    {ap}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ─── Analytics Section (Dynamically Calculated) ─── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Infrastructure Intelligence Metrics</h2>
            <p className="text-xs sm:text-sm text-[#737B8C] dark:text-[#929CB3] mt-0.5">
              Active graph spectrum, resilience scores and topological parameters for <span className="font-semibold text-slate-900 dark:text-[#F5F7FF] font-mono-code">{selectedNetwork.name}</span>
            </p>
          </div>
          <button
            onClick={onNavigateToAnalytics}
            className="text-xs font-semibold text-[#6366F1] dark:text-cyan-400 hover:text-indigo-700 dark:hover:text-cyan-300 flex items-center gap-1.5 cursor-pointer bg-indigo-50/80 dark:bg-[#121A2B] hover:bg-indigo-100/80 dark:hover:bg-[#182238] px-3.5 py-2 rounded-xl border border-indigo-200/80 dark:border-[#253149] transition-colors"
          >
            <span>Full Spectral Analysis</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          <MetricItem
            label="Total Nodes"
            value={nodeCount}
            subtext="Vertices in network |V|"
            icon={<NetworkIcon className="w-4 h-4 text-[#3B82F6] dark:text-[#4F8CFF]" />}
          />
          <MetricItem
            label="Active Connections"
            value={edgeCount}
            subtext="Undirected communication links |E|"
            icon={<GitFork className="w-4 h-4 text-[#6366F1] dark:text-[#9B7BFF]" />}
          />
          <MetricItem
            label="Critical Components"
            value={apCount + bridgeCount}
            subtext={`${apCount} nodes · ${bridgeCount} bridges`}
            trend={apCount + bridgeCount > 0 ? 'critical' : 'healthy'}
            icon={<ShieldAlert className="w-4 h-4 text-[#FF784F]" />}
          />
          <MetricItem
            label="Connected Subgraphs"
            value={componentCount}
            subtext={componentCount === 1 ? 'Unified topology (k=1)' : `Partitioned (${componentCount} islands)`}
            trend={componentCount === 1 ? 'healthy' : 'critical'}
            icon={<Activity className="w-4 h-4 text-emerald-600 dark:text-[#20D6A0]" />}
          />
          <MetricItem
            label="Current Resilience"
            value={`${(lccRatio * 100).toFixed(1)}%`}
            subtext={`LCC giant component size`}
            trend={lccRatio > 0.8 ? 'healthy' : 'critical'}
            icon={<CheckCircle2 className="w-4 h-4 text-[#22D3EE]" />}
          />
          <MetricItem
            label="Algebraic Conn (λ2)"
            value={algebraicConn}
            subtext="Laplacian spectral gap"
            trend={typeof analysis?.algebraic_connectivity === 'number' && analysis.algebraic_connectivity > 0.1 ? 'healthy' : 'warning'}
            icon={<Activity className="w-4 h-4 text-purple-500 dark:text-[#9B7BFF]" />}
          />
        </div>
      </div>

      {/* ─── Recent Activity Section (Display Actual Simulation Activity) ─── */}
      <div className="bg-white/90 dark:bg-[#0D1220]/92 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-3xl shadow-[0_4px_24px_-4px_rgba(0,0,0,0.03)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)] overflow-hidden transition-colors">
        <div className="px-6 py-5 border-b border-slate-100 dark:border-[#253149] flex items-center justify-between bg-slate-50/50 dark:bg-[#121A2B]/60">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-indigo-50 dark:bg-indigo-950/50 border border-indigo-200/80 dark:border-indigo-800/60 text-indigo-600 dark:text-[#9B7BFF]">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Recent Simulation Activity</h3>
              <p className="text-xs text-[#737B8C] dark:text-[#929CB3]">Actual deterministic failure executions and cascade runs</p>
            </div>
          </div>
          <Button size="sm" variant="brand" onClick={onNavigateToSimulation} icon={<Play className="w-3.5 h-3.5" />}>
            New Simulation
          </Button>
        </div>

        {recentSimulations.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 dark:bg-[#121A2B]/80 border-b border-slate-100 dark:border-[#253149] text-slate-500 dark:text-[#929CB3] font-mono-code uppercase text-[11px] font-semibold">
                <tr>
                  <th className="px-6 py-3.5">Simulation Run</th>
                  <th className="px-6 py-3.5">Type / Strategy</th>
                  <th className="px-6 py-3.5">Status</th>
                  <th className="px-6 py-3.5">LCC Retention</th>
                  <th className="px-6 py-3.5">Pairwise Conn</th>
                  <th className="px-6 py-3.5">Executed At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-[#253149] font-mono-code">
                {recentSimulations.slice(0, 6).map((sim) => (
                  <tr key={sim.id} className="hover:bg-slate-50/80 dark:hover:bg-[#182238]/60 transition-colors">
                    <td className="px-6 py-4 text-slate-900 dark:text-[#F5F7FF] font-bold">
                      {sim.id.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="cyan" size="sm">{sim.simulation_type}</Badge>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={sim.status === 'completed' ? 'healthy' : sim.status === 'failed' ? 'failed' : 'warning'} size="sm">
                        {sim.status}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-[#F5F7FF]">
                      {sim.results?.lcc_ratio !== undefined ? `${(sim.results.lcc_ratio * 100).toFixed(1)}%` : '—'}
                    </td>
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-[#F5F7FF]">
                      {sim.results?.pairwise_connectivity_ratio !== undefined
                        ? `${(sim.results.pairwise_connectivity_ratio * 100).toFixed(1)}%`
                        : '—'}
                    </td>
                    <td className="px-6 py-4 text-slate-500 dark:text-[#929CB3] font-sans">
                      {new Date(sim.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-sm text-[#737B8C] dark:text-[#929CB3]">
            No simulation activity recorded on this network yet. Launch a test scenario in the Simulation Lab to inspect mathematical degradation.
          </div>
        )}
      </div>
    </div>
  );
};
