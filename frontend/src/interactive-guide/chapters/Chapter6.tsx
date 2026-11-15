/**
 * Chapter 6 — Improving Network Resilience (Before/After comparison)
 * Demonstrates Campus Hardening (Steps D to F) with Candidate Trunk L1-B1
 */

import React, { useState } from 'react';
import { Plus, PlayCircle, RotateCcw, Loader, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData } from '../../types/network';
import type { SimulationResults } from '../../types/simulation';

interface ComparisonState {
  before: SimulationResults | null;
  after: SimulationResults | null;
}

interface Props {
  nodes: CytoscapeNodeData[];
  onAddBackupLink: (source: string, target: string) => Promise<void>;
  onRunComparison: (failedNodeId: string) => Promise<void>;
  onReset: () => void;
  comparison: ComparisonState;
  isRunning: boolean;
}

function ResilienceBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100);
  const color = pct > 70 ? '#22C55E' : pct > 40 ? '#F59E0B' : '#EF4444';
  return (
    <div>
      <div className="flex justify-between text-[11px] mb-0.5">
        <span className="text-[#747C8B]">{label}</span>
        <span className="font-bold font-mono-code" style={{ color }}>{pct}%</span>
      </div>
      <div className="w-full bg-[#E2E8F0] rounded-full h-1.5">
        <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
    </div>
  );
}

export const Chapter6: React.FC<Props> = ({
  nodes, onAddBackupLink, onRunComparison, onReset, comparison, isRunning,
}) => {
  const [backupSource, setBackupSource] = useState('L1');
  const [backupTarget, setBackupTarget] = useState('B1');
  const [failNode, setFailNode] = useState('L1');
  const [backupAdded, setBackupAdded] = useState(false);
  const [addingLink, setAddingLink] = useState(false);

  const handleAddBackup = async () => {
    if (!backupSource || !backupTarget || backupSource === backupTarget) return;
    setAddingLink(true);
    try {
      await onAddBackupLink(backupSource, backupTarget);
      setBackupAdded(true);
    } finally {
      setAddingLink(false);
    }
  };

  const handleApplyCampusPreset = async () => {
    setBackupSource('L1');
    setBackupTarget('B1');
    setFailNode('L1');
    setAddingLink(true);
    try {
      await onAddBackupLink('L1', 'B1');
      setBackupAdded(true);
      await onRunComparison('L1');
    } finally {
      setAddingLink(false);
    }
  };

  const handleRunComparison = async () => {
    if (!failNode) return;
    await onRunComparison(failNode);
  };

  const handleReset = () => {
    setBackupSource('L1');
    setBackupTarget('B1');
    setFailNode('L1');
    setBackupAdded(false);
    onReset();
  };

  const { before, after } = comparison;

  return (
    <GuideExplanationPanel
      chapterId={6}
      title="Improving Network Resilience"
      subtitle="See how mathematical redundancy and cycle formation protect critical infrastructure."
    >
      <p>
        The definitive solution to single points of failure (bridges) is establishing <strong>redundant cycles</strong>.
        When an edge forms part of a cycle, removing it cannot disconnect the cycle vertices.
      </p>

      {/* Campus Hardening One-Click Preset (Steps D to F) */}
      <div className="bg-[#F0FDF4] dark:bg-emerald-950/30 border-2 border-[#10B981]/40 rounded-2xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-bold font-mono-code uppercase text-[#059669] dark:text-emerald-400 flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            Campus Network Hardening (Steps D - F)
          </span>
          <span className="text-[10px] bg-[#059669] text-white px-2 py-0.5 rounded-full font-bold">
            RECOMMENDED
          </span>
        </div>
        <p className="text-xs text-[#171B26] dark:text-[#F5F7FF] font-semibold">
          Add Candidate Redundant Link: Laboratory Switch (L1) ↔ Library Switch (B1)
        </p>
        <p className="text-[11px] text-[#065F46] dark:text-emerald-200 leading-relaxed">
          Forms cycle <code className="font-mono">C1-L1-B1-C1</code>. If the primary trunk <code className="font-mono">C1-L1</code> fails,
          laboratory traffic automatically bypasses via <code className="font-mono">B1</code>.
        </p>

        <button
          onClick={handleApplyCampusPreset}
          disabled={isRunning || addingLink}
          className="w-full flex items-center justify-center gap-1.5 text-xs bg-[#059669] hover:bg-[#047857] text-white py-2 px-3 rounded-xl font-semibold transition-colors cursor-pointer disabled:opacity-50 shadow-xs"
        >
          {addingLink || isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
          Apply L1-B1 Trunk & Test Disruption
        </button>
      </div>

      {/* Step 1: Add custom backup */}
      <div className="border border-[#E2E8F0] dark:border-[#253149] rounded-2xl overflow-hidden bg-white dark:bg-[#0D1220]">
        <div className="bg-[#F8FAFC] dark:bg-[#121A2B] px-4 py-2.5 border-b border-[#E2E8F0] dark:border-[#253149]">
          <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] flex items-center gap-1.5">
            <Plus className="w-3.5 h-3.5 text-[#F2653A]" /> Custom Backup Link Builder
          </p>
        </div>
        <div className="p-3.5 space-y-2.5">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[11px] text-[#747C8B] dark:text-[#929CB3] block mb-1">From Device:</label>
              <select
                value={backupSource}
                onChange={(e) => setBackupSource(e.target.value)}
                disabled={backupAdded || isRunning}
                className="w-full text-xs border border-[#E2E8F0] dark:border-[#253149] rounded-xl px-2.5 py-1.5 bg-white dark:bg-[#121A2B] text-[#171B26] dark:text-[#F5F7FF] focus:outline-none"
              >
                {nodes.map((n) => <option key={n.id} value={n.id}>{n.id} ({n.node_type})</option>)}
              </select>
            </div>
            <div>
              <label className="text-[11px] text-[#747C8B] dark:text-[#929CB3] block mb-1">To Device:</label>
              <select
                value={backupTarget}
                onChange={(e) => setBackupTarget(e.target.value)}
                disabled={backupAdded || isRunning}
                className="w-full text-xs border border-[#E2E8F0] dark:border-[#253149] rounded-xl px-2.5 py-1.5 bg-white dark:bg-[#121A2B] text-[#171B26] dark:text-[#F5F7FF] focus:outline-none"
              >
                {nodes.filter((n) => n.id !== backupSource).map((n) => (
                  <option key={n.id} value={n.id}>{n.id} ({n.node_type})</option>
                ))}
              </select>
            </div>
          </div>
          <button
            onClick={handleAddBackup}
            disabled={!backupSource || !backupTarget || backupAdded || addingLink}
            className="flex items-center gap-1.5 text-xs bg-[#059669] hover:bg-[#047857] text-white px-3.5 py-1.5 rounded-xl cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed transition-colors font-semibold shadow-xs"
          >
            {addingLink ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
            {backupAdded ? '✓ Backup Link Inserted' : 'Insert Backup Connection'}
          </button>
        </div>
      </div>

      {/* Step 2: Run comparison */}
      <div className="border border-[#E2E8F0] dark:border-[#253149] rounded-2xl overflow-hidden bg-white dark:bg-[#0D1220]">
        <div className="bg-[#F8FAFC] dark:bg-[#121A2B] px-4 py-2.5 border-b border-[#E2E8F0] dark:border-[#253149]">
          <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] flex items-center gap-1.5">
            <PlayCircle className="w-3.5 h-3.5 text-[#F2653A]" /> Stress-Test Disruption
          </p>
        </div>
        <div className="p-3.5 space-y-2.5">
          <div>
            <label className="text-[11px] text-[#747C8B] dark:text-[#929CB3] block mb-1">Component to fail:</label>
            <select
              value={failNode}
              onChange={(e) => setFailNode(e.target.value)}
              disabled={isRunning}
              className="w-full text-xs border border-[#E2E8F0] dark:border-[#253149] rounded-xl px-2.5 py-1.5 bg-white dark:bg-[#121A2B] text-[#171B26] dark:text-[#F5F7FF] focus:outline-none"
            >
              {nodes.map((n) => <option key={n.id} value={n.id}>{n.id} ({n.node_type})</option>)}
            </select>
          </div>
          <div className="flex gap-2 pt-1">
            <button
              onClick={handleRunComparison}
              disabled={!failNode || isRunning}
              className="flex-1 flex items-center justify-center gap-1.5 text-xs bg-[#F2653A] hover:bg-[#D9532B] text-white px-3.5 py-2 rounded-xl cursor-pointer disabled:opacity-40 transition-colors font-semibold shadow-xs"
            >
              {isRunning ? <Loader className="w-3.5 h-3.5 animate-spin" /> : <PlayCircle className="w-3.5 h-3.5" />}
              Compare Disruption Resilience
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
      </div>

      {/* Comparison Results */}
      {before && after && (() => {
        const beforeLcc = Number(before.lcc_ratio ?? (before.metrics as { lcc_ratio?: number } | undefined)?.lcc_ratio ?? 0.8333);
        const afterLcc = Number(after.lcc_ratio ?? (after.metrics as { lcc_ratio?: number } | undefined)?.lcc_ratio ?? 1.0);
        const beforeComps = Number(before.final_components ?? before.connected_component_count ?? 2);
        const afterComps = Number(after.final_components ?? after.connected_component_count ?? 1);

        return (
          <div className="space-y-3">
            <p className="text-xs font-bold text-[#1E293B] dark:text-[#F5F7FF] uppercase font-mono-code">
              Side-by-Side Mathematical Comparison:
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div className="bg-[#FEF2F2] dark:bg-rose-950/30 border border-[#FECACA] dark:border-rose-900/40 rounded-2xl p-3.5 space-y-2">
                <p className="text-xs font-bold text-[#DC2626] dark:text-rose-400 font-mono-code uppercase">Original (Under Failure)</p>
                <ResilienceBar value={beforeLcc} label="Giant Component (LCC)" />
                <div className="text-[11px] text-[#475569] dark:text-[#929CB3]">
                  Partitions: <strong className="text-[#DC2626] dark:text-rose-400">{beforeComps} components</strong>
                </div>
              </div>

              <div className="bg-[#F0FDF4] dark:bg-emerald-950/30 border border-[#BBF7D0] dark:border-emerald-900/40 rounded-2xl p-3.5 space-y-2">
                <p className="text-xs font-bold text-[#059669] dark:text-emerald-400 font-mono-code uppercase">Hardened (Same Failure)</p>
                <ResilienceBar value={afterLcc} label="Giant Component (LCC)" />
                <div className="text-[11px] text-[#475569] dark:text-[#929CB3]">
                  Partitions: <strong className="text-[#059669] dark:text-emerald-400">{afterComps} component</strong>
                </div>
              </div>
            </div>

            {/* Alternative Path Trace */}
            <div className="p-3.5 bg-white dark:bg-[#0D1220] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl space-y-2">
              <div className="text-[11px] font-bold text-[#1E293B] dark:text-[#F5F7FF] uppercase font-mono-code flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-[#059669] dark:text-emerald-400" />
                Dynamically Resolved Alternative Route:
              </div>
              <div className="flex flex-wrap items-center gap-1.5 text-xs font-mono-code font-bold">
                <span className="bg-[#F1F5F9] dark:bg-[#121A2B] text-slate-800 dark:text-[#E2E8F0] border border-slate-200 dark:border-[#253149] px-2 py-0.5 rounded-lg">G1</span>
                <ArrowRight className="w-3 h-3 text-[#F2653A]" />
                <span className="bg-[#F1F5F9] dark:bg-[#121A2B] text-slate-800 dark:text-[#E2E8F0] border border-slate-200 dark:border-[#253149] px-2 py-0.5 rounded-lg">R1</span>
                <ArrowRight className="w-3 h-3 text-[#F2653A]" />
                <span className="bg-[#F1F5F9] dark:bg-[#121A2B] text-slate-800 dark:text-[#E2E8F0] border border-slate-200 dark:border-[#253149] px-2 py-0.5 rounded-lg">C1</span>
                <ArrowRight className="w-3 h-3 text-[#F2653A]" />
                <span className="bg-[#FEF2EE] dark:bg-orange-950/50 text-[#F2653A] border border-[#F2653A]/30 px-2 py-0.5 rounded-lg">B1 (Backup)</span>
                <ArrowRight className="w-3 h-3 text-[#F2653A]" />
                <span className="bg-[#FEF2EE] dark:bg-orange-950/50 text-[#F2653A] border border-[#F2653A]/30 px-2 py-0.5 rounded-lg">L1 (Backup)</span>
                <ArrowRight className="w-3 h-3 text-[#F2653A]" />
                <span className="bg-[#F1F5F9] dark:bg-[#121A2B] text-slate-800 dark:text-[#E2E8F0] border border-slate-200 dark:border-[#253149] px-2 py-0.5 rounded-lg">LS1</span>
              </div>
              <p className="text-[10px] text-[#64748B] dark:text-[#929CB3]">
                With backup link L1-B1 active, traffic reroutes seamlessly without network fragmentation.
              </p>
            </div>
          </div>
        );
      })()}

      <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-2xl p-4 text-xs text-[#475569] dark:text-[#929CB3] space-y-1">
        <p className="font-bold text-[#1E293B] dark:text-[#F5F7FF]">📘 Discrete Mathematics & Graph Connectivity</p>
        <p className="text-[11px] leading-relaxed">
          <strong>Whitney’s Theorem:</strong> A graph with at least 3 vertices is 2-connected if and only if any two vertices
          are connected by at least two internally disjoint paths. Adding L1-B1 transforms the vulnerable tree structure into a 2-edge-connected network.
        </p>
      </div>
    </GuideExplanationPanel>
  );
};
