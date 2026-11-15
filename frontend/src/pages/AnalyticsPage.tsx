import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  RefreshCw,
  Activity,
  ShieldAlert,
  GitFork,
  Sparkles
} from 'lucide-react';
import type { Network } from '../types/network';
import type { 
  ConnectivityAnalysis, 
  NodeCriticalityItem, 
  EdgeCriticalityItem 
} from '../types/analytics';
import { 
  analyzeNetwork, 
  fetchNodeCriticality, 
  fetchEdgeCriticality, 
  generateResilienceReport 
} from '../services/analyticsService';
import { ResilienceCharts } from '../components/analytics/ResilienceCharts';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { MetricItem } from '../components/common/MetricItem';

export interface AnalyticsPageProps {
  selectedNetwork: Network | null;
  onSelectNodeInTopology?: (nodeId: string) => void;
  onOpenReportModal?: (markdown: string, networkName: string) => void;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({
  selectedNetwork,
  onSelectNodeInTopology,
  onOpenReportModal
}) => {
  const [analysis, setAnalysis] = useState<ConnectivityAnalysis | null>(null);
  const [nodeCriticality, setNodeCriticality] = useState<NodeCriticalityItem[]>([]);
  const [edgeCriticality, setEdgeCriticality] = useState<EdgeCriticalityItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [activeTab, setActiveTab] = useState<'nodes' | 'edges'>('nodes');

  const loadAnalyticsData = async () => {
    if (!selectedNetwork) return;
    setIsLoading(true);
    try {
      const [analysisRes, nodesRes, edgesRes] = await Promise.all([
        analyzeNetwork(selectedNetwork.id),
        fetchNodeCriticality(selectedNetwork.id),
        fetchEdgeCriticality(selectedNetwork.id)
      ]);
      setAnalysis(analysisRes);
      setNodeCriticality(nodesRes);
      setEdgeCriticality(edgesRes);
    } catch {
      // Fallback
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAnalyticsData();
  }, [selectedNetwork?.id]);

  const handleGenerateReport = async () => {
    if (!selectedNetwork) return;
    setIsGeneratingReport(true);
    try {
      const reportRes = await generateResilienceReport(selectedNetwork.id);
      if (onOpenReportModal) {
        onOpenReportModal(reportRes.markdown_report, reportRes.network_name);
      }
    } catch {
      alert('Unable to generate resilience audit report.');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  if (!selectedNetwork) {
    return (
      <div className="p-12 text-center bg-white/95 dark:bg-[#0D1220]/95 border border-slate-200/90 dark:border-[#253149] rounded-3xl shadow-xl max-w-4xl mx-auto my-12 text-[#171923] dark:text-[#F5F7FF]">
        <Activity className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-[#171923] dark:text-[#F5F7FF]">No Active Network Selected</h3>
        <p className="text-sm text-[#737B8C] dark:text-[#929CB3] mt-1.5">Please select an infrastructure network to run resilience analytics.</p>
      </div>
    );
  }

  const nodeCount = analysis?.node_count ?? selectedNetwork.node_count;
  const edgeCount = analysis?.edge_count ?? selectedNetwork.edge_count;
  const avgDegree = nodeCount > 0 ? ((2 * edgeCount) / nodeCount).toFixed(2) : '0.00';
  const density = analysis?.density !== undefined ? `${(analysis.density * 100).toFixed(1)}%` : '0.0%';
  const apCount = analysis?.articulation_points.length ?? 0;
  const bridgeCount = analysis?.bridges.length ?? 0;
  const lccRatio = analysis?.lcc_ratio !== undefined ? `${(analysis.lcc_ratio * 100).toFixed(1)}%` : '100.0%';
  const algebraicConn = analysis?.algebraic_connectivity !== undefined ? analysis.algebraic_connectivity.toFixed(4) : 'N/A';

  return (
    <div className="space-y-8 pb-10">
      {/* Header Banner */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-6 shadow-xs flex flex-wrap items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl font-extrabold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Resilience Analytics & Spectral Intelligence</h2>
            <Badge variant="brand">Graph Laplacian Spectrum</Badge>
          </div>
          <p className="text-xs sm:text-sm text-[#737B8C] dark:text-[#929CB3] mt-1">
            Algebraic connectivity, articulation cut-vertices, bridge links, and centrality ranking for <span className="font-semibold text-slate-900 dark:text-[#F5F7FF] font-mono-code">{selectedNetwork.name}</span>.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="sm"
            icon={<RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />}
            onClick={loadAnalyticsData}
            disabled={isLoading}
          >
            Recalculate
          </Button>
          <Button
            variant="brand"
            size="sm"
            icon={<FileText className="w-3.5 h-3.5 text-white" />}
            onClick={handleGenerateReport}
            isLoading={isGeneratingReport}
          >
            Export Resilience Audit
          </Button>
        </div>
      </div>

      {/* Primary Resilience KPI Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricItem
          label="Density 2|E|/|V|(|V|-1)"
          value={density}
          subtext="Link saturation"
          trend={density === '0.0%' ? 'neutral' : 'healthy'}
          icon={<GitFork className="w-4 h-4 text-[#3B82F6] dark:text-[#4F8CFF]" />}
        />
        <MetricItem
          label="Average Degree"
          value={avgDegree}
          subtext="mean links per vertex"
          trend="neutral"
          icon={<Activity className="w-4 h-4 text-indigo-500 dark:text-[#9B7BFF]" />}
        />
        <MetricItem
          label="LCC Giant Ratio"
          value={lccRatio}
          subtext={`${analysis?.largest_component_size ?? nodeCount}/${nodeCount} nodes online`}
          trend={analysis?.lcc_ratio && analysis.lcc_ratio < 0.8 ? 'critical' : 'healthy'}
          icon={<ShieldAlert className="w-4 h-4 text-[#22D3EE]" />}
        />
        <MetricItem
          label="Algebraic Conn (λ2)"
          value={algebraicConn}
          subtext="Laplacian spectral gap"
          trend={typeof analysis?.algebraic_connectivity === 'number' && analysis.algebraic_connectivity > 0.1 ? 'healthy' : 'warning'}
          icon={<Sparkles className="w-4 h-4 text-purple-500 dark:text-[#9B7BFF]" />}
        />
        <MetricItem
          label="Critical Vertices"
          value={apCount}
          subtext="Articulation cut-points"
          trend={apCount > 0 ? 'critical' : 'healthy'}
          icon={<ShieldAlert className="w-4 h-4 text-[#FF784F]" />}
        />
        <MetricItem
          label="Critical Bridges"
          value={bridgeCount}
          subtext="Cut-edges in network"
          trend={bridgeCount > 0 ? 'warning' : 'healthy'}
          icon={<GitFork className="w-4 h-4 text-amber-500 dark:text-[#F6BD60]" />}
        />
      </div>

      {/* Recharts Analytics Dashboard Visualizers */}
      <ResilienceCharts
        criticalNodes={nodeCriticality}
      />

      {/* Criticality Ranking Data Table */}
      <Card
        header={
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 className="text-base font-bold text-[#171923] dark:text-[#F5F7FF] tracking-tight">
                Topological Centrality & Impact Ranking
              </h3>
              <p className="text-xs text-[#737B8C] dark:text-[#929CB3]">Discrete components sorted by structural vulnerability</p>
            </div>
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-[#121A2B] p-1 rounded-xl border border-slate-200 dark:border-[#253149]">
              <button
                onClick={() => setActiveTab('nodes')}
                className={`px-3.5 py-1.5 text-xs rounded-lg font-semibold cursor-pointer transition-all ${
                  activeTab === 'nodes' 
                    ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs' 
                    : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
                }`}
              >
                Nodes ({nodeCriticality.length})
              </button>
              <button
                onClick={() => setActiveTab('edges')}
                className={`px-3.5 py-1.5 text-xs rounded-lg font-semibold cursor-pointer transition-all ${
                  activeTab === 'edges' 
                    ? 'bg-white dark:bg-[#182238] text-slate-900 dark:text-[#F5F7FF] shadow-xs' 
                    : 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
                }`}
              >
                Edges ({edgeCriticality.length})
              </button>
            </div>
          </div>
        }
      >
        {activeTab === 'nodes' ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono-code">
              <thead className="bg-slate-50/80 dark:bg-[#121A2B]/80 border-b border-slate-100 dark:border-[#253149] text-slate-500 dark:text-[#929CB3] uppercase text-[11px] font-semibold">
                <tr>
                  <th className="px-5 py-3.5">Component ID</th>
                  <th className="px-5 py-3.5">Degree</th>
                  <th className="px-5 py-3.5">Betweenness</th>
                  <th className="px-5 py-3.5">Cut-Vertex (AP)</th>
                  <th className="px-5 py-3.5">Δ Connectivity Impact</th>
                  <th className="px-5 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-[#253149]">
                {nodeCriticality.map((n) => (
                  <tr key={n.node_id} className="hover:bg-slate-50/80 dark:hover:bg-[#182238]/60 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-slate-900 dark:text-[#F5F7FF]">{n.node_id}</td>
                    <td className="px-5 py-3.5 text-slate-700 dark:text-slate-300">{n.degree}</td>
                    <td className="px-5 py-3.5 text-slate-700 dark:text-slate-300">{(n.betweenness ?? n.criticality_score ?? 0).toFixed(4)}</td>
                    <td className="px-5 py-3.5">
                      <Badge variant={n.is_articulation_point ? 'critical' : 'neutral'} size="sm">
                        {n.is_articulation_point ? 'SPOF Cut-Vertex' : 'Regular'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-[#FF784F]">{((n.connectivity_drop || 0) * 100).toFixed(1)}%</span>
                        <div className="w-20 bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
                          <div 
                            className="bg-[#FF784F] h-full rounded-full" 
                            style={{ width: `${Math.min(100, (n.connectivity_drop || 0) * 100)}%` }} 
                          />
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-right font-sans">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onSelectNodeInTopology?.(n.node_id)}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono-code">
              <thead className="bg-slate-50/80 dark:bg-[#121A2B]/80 border-b border-slate-100 dark:border-[#253149] text-slate-500 dark:text-[#929CB3] uppercase text-[11px] font-semibold">
                <tr>
                  <th className="px-5 py-3.5">Link ID</th>
                  <th className="px-5 py-3.5">Endpoints</th>
                  <th className="px-5 py-3.5">Betweenness</th>
                  <th className="px-5 py-3.5">Bridge Status</th>
                  <th className="px-5 py-3.5">Δ Connectivity Impact</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-[#253149]">
                {edgeCriticality.map((e) => (
                  <tr key={e.edge_id} className="hover:bg-slate-50/80 dark:hover:bg-[#182238]/60 transition-colors">
                    <td className="px-5 py-3.5 font-bold text-slate-900 dark:text-[#F5F7FF]">{e.edge_id}</td>
                    <td className="px-5 py-3.5 text-slate-700 dark:text-slate-300">{e.source} ↔ {e.target}</td>
                    <td className="px-5 py-3.5 text-slate-700 dark:text-slate-300">{(e.betweenness ?? e.criticality_score ?? 0).toFixed(4)}</td>
                    <td className="px-5 py-3.5">
                      <Badge variant={e.is_bridge ? 'critical' : 'neutral'} size="sm">
                        {e.is_bridge ? 'Bridge Cut-Edge' : 'Redundant'}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-bold text-amber-600 dark:text-[#F6BD60]">{((e.connectivity_drop || 0) * 100).toFixed(1)}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
