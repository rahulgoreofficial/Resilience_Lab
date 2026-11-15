import React, { useState } from 'react';
import { 
  GitCompare, 
  Play, 
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import type { Network, NetworkTopologyResponse } from '../types/network';
import type { ScenarioComparisonResponse } from '../types/analytics';
import { compareScenarios } from '../services/analyticsService';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';

export interface ComparisonPageProps {
  selectedNetwork: Network | null;
  topology: NetworkTopologyResponse | null;
}

export const ComparisonPage: React.FC<ComparisonPageProps> = ({
  selectedNetwork,
  topology
}) => {
  const [scenarioAName, setScenarioAName] = useState('Scenario A (Perimeter Breach)');
  const [scenarioBName, setScenarioBName] = useState('Scenario B (Core Switch Failure)');
  const [scenarioANodes, setScenarioANodes] = useState<string[]>([]);
  const [scenarioBNodes, setScenarioBNodes] = useState<string[]>([]);
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<ScenarioComparisonResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const allNodes = topology?.elements.nodes || [];

  const handleRunComparison = async () => {
    if (!selectedNetwork) return;
    setIsComparing(true);
    setErrorMessage(null);
    try {
      const res = await compareScenarios(selectedNetwork.id, [
        { name: scenarioAName, failed_node_ids: scenarioANodes },
        { name: scenarioBName, failed_node_ids: scenarioBNodes }
      ]);
      setComparisonResult(res);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Comparison failed.');
    } finally {
      setIsComparing(false);
    }
  };

  const handleLoadPreset = (preset: 'core_vs_edge' | 'single_vs_double') => {
    if (preset === 'core_vs_edge') {
      const core = allNodes.find((n) => n.data.node_type === 'router' || n.data.id.includes('C1') || n.data.id.includes('R1'));
      const edge = allNodes.find((n) => n.data.node_type === 'switch' && n.data.id !== core?.data.id);
      setScenarioAName('Core Failure Hypothesis');
      setScenarioBName('Edge Subnet Failure');
      setScenarioANodes(core ? [core.data.id] : []);
      setScenarioBNodes(edge ? [edge.data.id] : []);
    } else {
      if (allNodes.length >= 2) {
        setScenarioAName('Single Point Outage');
        setScenarioBName('Concurrent Dual-Point Outage');
        setScenarioANodes([allNodes[0].data.id]);
        setScenarioBNodes([allNodes[0].data.id, allNodes[1].data.id]);
      }
    }
  };

  if (!selectedNetwork) {
    return (
      <div className="p-12 text-center bg-white/95 dark:bg-[#0D1220]/95 border border-slate-200/90 dark:border-[#253149] rounded-3xl shadow-xl max-w-4xl mx-auto my-12 text-[#171923] dark:text-[#F5F7FF]">
        <GitCompare className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <h3 className="text-xl font-bold text-[#171923] dark:text-[#F5F7FF]">No Active Network Selected</h3>
        <p className="text-sm text-[#737B8C] dark:text-[#929CB3] mt-1.5">Please select an infrastructure network to run scenario comparisons.</p>
      </div>
    );
  }

  const scA = comparisonResult?.scenarios[0];
  const scB = comparisonResult?.scenarios[1];
  const deltaLcc = scA && scB ? ((scB.lcc_ratio - scA.lcc_ratio) * 100).toFixed(1) : null;
  const deltaPairwise = scA && scB ? ((scB.pairwise_connectivity - scA.pairwise_connectivity) * 100).toFixed(1) : null;

  return (
    <div className="space-y-8 pb-10">
      {/* Header Banner */}
      <div className="bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl p-6 shadow-xs flex flex-wrap items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-xl font-extrabold text-[#171923] dark:text-[#F5F7FF] tracking-tight">Scenario Comparison Laboratory</h2>
            <Badge variant="brand">Differential Analysis</Badge>
          </div>
          <p className="text-xs sm:text-sm text-[#737B8C] dark:text-[#929CB3] mt-1">
            Evaluate competing failure hypotheses and redundancy architectures side-by-side on <span className="font-semibold text-slate-900 dark:text-[#F5F7FF] font-mono-code">{selectedNetwork.name}</span>.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleLoadPreset('core_vs_edge')}
          >
            Preset: Core vs Edge
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleLoadPreset('single_vs_double')}
          >
            Preset: Single vs Dual
          </Button>
          <Button
            variant="brand"
            size="sm"
            icon={<Play className="w-3.5 h-3.5 text-white" />}
            onClick={handleRunComparison}
            isLoading={isComparing}
          >
            Compare Scenarios
          </Button>
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 bg-rose-50/90 dark:bg-rose-950/30 border border-rose-200/90 dark:border-rose-500/40 rounded-2xl text-xs text-[#FF784F] dark:text-[#FF5364] flex items-center justify-between shadow-2xs transition-colors">
          <div className="flex items-center gap-2.5 font-medium">
            <AlertTriangle className="w-4 h-4 shrink-0 text-[#FF784F]" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="underline cursor-pointer font-semibold">Dismiss</button>
        </div>
      )}

      {/* Scenario Input Configuration Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Scenario A Card */}
        <div className="bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border border-slate-200/90 dark:border-[#253149] rounded-3xl p-6 shadow-sm space-y-4 text-[#171923] dark:text-[#F5F7FF] transition-colors">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-[#253149] pb-3.5">
            <div className="flex items-center gap-2.5">
              <span className="w-7 h-7 rounded-xl bg-orange-50 dark:bg-rose-950/50 text-[#FF784F] flex items-center justify-center font-bold text-xs font-mono-code border border-orange-200/80 dark:border-rose-800/60">
                A
              </span>
              <input
                type="text"
                value={scenarioAName}
                onChange={(e) => setScenarioAName(e.target.value)}
                className="font-bold text-sm text-slate-900 dark:text-[#F5F7FF] bg-transparent focus:outline-none border-b border-transparent focus:border-[#FF784F]"
              />
            </div>
            <Badge variant="critical" size="sm">{scenarioANodes.length} Failed</Badge>
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-slate-500 dark:text-[#929CB3] font-mono-code uppercase">Toggle Offline Nodes:</span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-48 overflow-y-auto p-2 bg-slate-50 dark:bg-[#121A2B]/60 border border-slate-200 dark:border-[#253149] rounded-2xl">
              {allNodes.map((n) => {
                const isSelected = scenarioANodes.includes(n.data.id);
                return (
                  <button
                    key={n.data.id}
                    type="button"
                    onClick={() => {
                      if (isSelected) setScenarioANodes(scenarioANodes.filter((id) => id !== n.data.id));
                      else setScenarioANodes([...scenarioANodes, n.data.id]);
                    }}
                    className={`p-2 rounded-xl text-xs font-mono-code text-left border cursor-pointer transition-all ${
                      isSelected 
                        ? 'bg-rose-50 dark:bg-rose-950/40 border-[#FF784F] text-[#FF784F] font-bold shadow-2xs' 
                        : 'bg-white dark:bg-[#182238] border-slate-200 dark:border-[#253149] text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <span className="truncate">{n.data.id}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Scenario B Card */}
        <div className="bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border border-slate-200/90 dark:border-[#253149] rounded-3xl p-6 shadow-sm space-y-4 text-[#171923] dark:text-[#F5F7FF] transition-colors">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-[#253149] pb-3.5">
            <div className="flex items-center gap-2.5">
              <span className="w-7 h-7 rounded-xl bg-cyan-50 dark:bg-cyan-950/50 text-cyan-600 dark:text-[#22D3EE] flex items-center justify-center font-bold text-xs font-mono-code border border-cyan-200/80 dark:border-cyan-800/60">
                B
              </span>
              <input
                type="text"
                value={scenarioBName}
                onChange={(e) => setScenarioBName(e.target.value)}
                className="font-bold text-sm text-slate-900 dark:text-[#F5F7FF] bg-transparent focus:outline-none border-b border-transparent focus:border-cyan-500"
              />
            </div>
            <Badge variant="cyan" size="sm">{scenarioBNodes.length} Failed</Badge>
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-slate-500 dark:text-[#929CB3] font-mono-code uppercase">Toggle Offline Nodes:</span>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-48 overflow-y-auto p-2 bg-slate-50 dark:bg-[#121A2B]/60 border border-slate-200 dark:border-[#253149] rounded-2xl">
              {allNodes.map((n) => {
                const isSelected = scenarioBNodes.includes(n.data.id);
                return (
                  <button
                    key={n.data.id}
                    type="button"
                    onClick={() => {
                      if (isSelected) setScenarioBNodes(scenarioBNodes.filter((id) => id !== n.data.id));
                      else setScenarioBNodes([...scenarioBNodes, n.data.id]);
                    }}
                    className={`p-2 rounded-xl text-xs font-mono-code text-left border cursor-pointer transition-all ${
                      isSelected 
                        ? 'bg-cyan-50 dark:bg-cyan-950/40 border-cyan-500 dark:border-cyan-400 text-cyan-700 dark:text-cyan-300 font-bold shadow-2xs' 
                        : 'bg-white dark:bg-[#182238] border-slate-200 dark:border-[#253149] text-slate-700 dark:text-slate-300'
                    }`}
                  >
                    <span className="truncate">{n.data.id}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Comparison Results Card */}
      {comparisonResult && scA && scB && (
        <Card
          header={
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-base font-bold text-slate-900 dark:text-[#F5F7FF] tracking-tight">Differential Outcome Breakdown</h3>
                <p className="text-xs text-slate-400 dark:text-[#69758E] font-mono-code">Mathematical contrast between Scenario A and Scenario B</p>
              </div>
              <Badge variant="healthy" size="sm">Calculated</Badge>
            </div>
          }
        >
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-[#929CB3] font-mono-code uppercase">LCC Retention Contrast</span>
              <div className="flex items-center justify-between mt-2 font-mono-code">
                <span className="text-xl font-bold text-[#FF784F]">{(scA.lcc_ratio * 100).toFixed(1)}% (A)</span>
                <span className="text-xl font-bold text-cyan-600 dark:text-cyan-400">{(scB.lcc_ratio * 100).toFixed(1)}% (B)</span>
              </div>
              <div className="mt-2 text-xs font-semibold font-mono-code text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                {parseFloat(deltaLcc || '0') >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-[#20D6A0]" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-rose-600 dark:text-[#FF5364]" />
                )}
                <span>Δ LCC = {deltaLcc}%</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-[#929CB3] font-mono-code uppercase">Pairwise Connectivity</span>
              <div className="flex items-center justify-between mt-2 font-mono-code">
                <span className="text-xl font-bold text-[#FF784F]">{(scA.pairwise_connectivity * 100).toFixed(1)}% (A)</span>
                <span className="text-xl font-bold text-cyan-600 dark:text-cyan-400">{(scB.pairwise_connectivity * 100).toFixed(1)}% (B)</span>
              </div>
              <div className="mt-2 text-xs font-semibold font-mono-code text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                <span>Δ Pairs = {deltaPairwise}%</span>
              </div>
            </div>

            <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl">
              <span className="text-[11px] font-semibold text-slate-500 dark:text-[#929CB3] font-mono-code uppercase">Component Partitioning</span>
              <div className="flex items-center justify-between mt-2 font-mono-code">
                <span className="text-xl font-bold text-[#FF784F]">{scA.connected_components ?? 'Multiple'} subgraphs</span>
                <span className="text-xl font-bold text-cyan-600 dark:text-cyan-400">{scB.connected_components ?? 'Multiple'} subgraphs</span>
              </div>
              <div className="mt-2 text-xs text-slate-500 dark:text-[#929CB3] font-mono-code">
                {(scA.connected_components ?? 0) > (scB.connected_components ?? 0) 
                  ? 'Scenario A produces greater fragmentation' 
                  : (scA.connected_components ?? 0) < (scB.connected_components ?? 0) 
                  ? 'Scenario B produces greater fragmentation' 
                  : 'Identical component fragmentation'}
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
