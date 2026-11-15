/**
 * Chapter 3 — Finding Critical Components (Articulation Points & Bridges)
 */

import React from 'react';
import { AlertTriangle, Link2 } from 'lucide-react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData } from '../../types/network';
import type { ConnectivityAnalysis } from '../../types/analytics';

interface Props {
  nodes: CytoscapeNodeData[];
  analysis: ConnectivityAnalysis | null;
  selectedNodeId: string | null;
  onHighlightArticulationPoints: () => void;
  onHighlightBridges: () => void;
}

export const Chapter3: React.FC<Props> = ({
  nodes, analysis, selectedNodeId, onHighlightArticulationPoints, onHighlightBridges,
}) => {
  const selectedIsAP = analysis?.articulation_points.includes(selectedNodeId ?? '') ?? false;

  return (
    <GuideExplanationPanel
      chapterId={3}
      title="Finding Critical Components"
      subtitle="Which devices are most dangerous to lose?"
    >
      <p>
        Not all devices are equally important. Some are so central that removing them
        <strong> breaks the network into disconnected pieces</strong>. We call these <em>critical components</em>.
      </p>

      <div className="space-y-3">
        <div className="bg-[#FFFBEB] dark:bg-amber-950/30 border border-[#FDE68A] dark:border-amber-800/40 rounded-xl p-3.5">
          <p className="flex items-center gap-2 font-semibold text-[#92400E] dark:text-amber-300 text-xs mb-1">
            <AlertTriangle className="w-4 h-4 text-amber-500" /> Articulation Points (Cut Vertices)
          </p>
          <p className="text-xs text-[#78350F] dark:text-amber-200">
            A device whose removal <strong>disconnects</strong> the network into separate groups.
          </p>
          {analysis ? (
            <div className="mt-2">
              {analysis.articulation_points.length > 0 ? (
                <>
                  <p className="text-xs font-medium text-[#92400E] dark:text-amber-300">Found {analysis.articulation_points.length} in this network:</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {analysis.articulation_points.map((id) => (
                      <span key={id} className="text-[11px] bg-[#FEF3C7] dark:bg-amber-900/50 text-[#92400E] dark:text-amber-200 px-2 py-0.5 rounded font-mono border border-[#FDE68A] dark:border-amber-700/50">{id}</span>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-xs text-[#059669] dark:text-emerald-400 mt-1">✓ No articulation points — robust topology!</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-[#94A3B8] dark:text-[#69758E] mt-1">Loading analysis…</p>
          )}
          <button
            onClick={onHighlightArticulationPoints}
            className="mt-2.5 text-xs bg-[#F59E0B] hover:bg-[#D97706] text-white px-3 py-1.5 rounded-lg cursor-pointer transition-colors shadow-2xs font-semibold"
          >
            Highlight in 3D View
          </button>
        </div>

        <div className="bg-[#FFF1F2] dark:bg-rose-950/30 border border-[#FECDD3] dark:border-rose-900/40 rounded-xl p-3.5">
          <p className="flex items-center gap-2 font-semibold text-[#9F1239] dark:text-rose-300 text-xs mb-1">
            <Link2 className="w-4 h-4 text-rose-500" /> Bridges (Cut Edges)
          </p>
          <p className="text-xs text-[#881337] dark:text-rose-200">
            A connection whose removal <strong>disconnects</strong> the network into separate groups.
          </p>
          {analysis ? (
            <div className="mt-2">
              {analysis.bridges.length > 0 ? (
                <>
                  <p className="text-xs font-medium text-[#9F1239] dark:text-rose-300">Found {analysis.bridges.length} bridge(s):</p>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {analysis.bridges.map(([s, t], i) => (
                      <span key={i} className="text-[11px] bg-[#FFE4E6] dark:bg-rose-900/50 text-[#9F1239] dark:text-rose-200 px-2 py-0.5 rounded font-mono border border-[#FECDD3] dark:border-rose-700/50">{s}↔{t}</span>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-xs text-[#059669] dark:text-emerald-400 mt-1">✓ No bridges — all connections are redundant!</p>
              )}
            </div>
          ) : (
            <p className="text-xs text-[#94A3B8] dark:text-[#69758E] mt-1">Loading analysis…</p>
          )}
          <button
            onClick={onHighlightBridges}
            className="mt-2.5 text-xs bg-[#EF4444] hover:bg-[#DC2626] text-white px-3 py-1.5 rounded-lg cursor-pointer transition-colors shadow-2xs font-semibold"
          >
            Highlight in 3D View
          </button>
        </div>
      </div>

      {selectedNodeId && selectedIsAP && (
        <div className="bg-[#FFFBEB] dark:bg-amber-950/30 border border-[#FCD34D] dark:border-amber-800/40 rounded-xl p-3 text-xs text-[#92400E] dark:text-amber-200">
          <p className="font-semibold">Selected node <code>{selectedNodeId}</code> is an ARTICULATION POINT</p>
          <p className="mt-1">If this device fails, the network will split into {(analysis?.connected_components_count ?? 1) + 1} isolated groups.</p>
        </div>
      )}

      {/* Network metrics */}
      {analysis && (
        <div className="grid grid-cols-2 gap-2 text-[11px]">
          <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-xl p-3">
            <p className="text-[#747C8B] dark:text-[#929CB3]">Connected Components</p>
            <p className="font-bold text-[#171B26] dark:text-[#F5F7FF] text-base">{analysis.connected_components_count}</p>
          </div>
          <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-xl p-3">
            <p className="text-[#747C8B] dark:text-[#929CB3]">Currently Connected?</p>
            <p className={`font-bold text-base ${analysis.is_connected ? 'text-[#059669] dark:text-emerald-400' : 'text-[#EF4444] dark:text-rose-400'}`}>
              {analysis.is_connected ? 'Yes ✓' : 'No ✗'}
            </p>
          </div>
          <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-xl p-3">
            <p className="text-[#747C8B] dark:text-[#929CB3]">LCC Size</p>
            <p className="font-bold text-[#171B26] dark:text-[#F5F7FF] text-base">{analysis.largest_component_size}/{nodes.length}</p>
          </div>
          <div className="bg-[#F8FAFC] dark:bg-[#121A2B] border border-[#E2E8F0] dark:border-[#253149] rounded-xl p-3">
            <p className="text-[#747C8B] dark:text-[#929CB3]">Graph Density</p>
            <p className="font-bold text-[#171B26] dark:text-[#F5F7FF] text-base">{(analysis.density * 100).toFixed(1)}%</p>
          </div>
        </div>
      )}

      <div className="bg-[#FEF2EE] dark:bg-orange-950/30 border border-[#FECDB0] dark:border-orange-800/40 rounded-xl p-3 text-xs text-[#7C2D12] dark:text-orange-200">
        <p className="font-semibold mb-1">💡 Key Insight</p>
        <p>
          Identifying articulation points uses <strong>Tarjan's Algorithm</strong> — a DFS-based
          algorithm from Discrete Mathematics. It finds these critical nodes in O(V + E) time.
        </p>
      </div>
    </GuideExplanationPanel>
  );
};
