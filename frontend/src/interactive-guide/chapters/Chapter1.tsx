/**
 * Chapter 1 — Understanding a Network
 */

import React, { useMemo } from 'react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData } from '../../types/network';

interface Props {
  nodes: CytoscapeNodeData[];
  selectedNodeId: string | null;
}

const NODE_ANALOGIES: Record<string, { emoji: string; analogy: string; role: string }> = {
  gateway:  { emoji: '🏙️', analogy: 'The main entrance to a city — all traffic enters here.', role: 'Connects the internal network to the outside world.' },
  firewall: { emoji: '🛡️', analogy: 'A security checkpoint at the city entrance — inspects all entering traffic.', role: 'Filters and blocks unwanted or dangerous traffic.' },
  router:   { emoji: '🚦', analogy: 'A road junction that directs traffic in the right direction.', role: 'Forwards data packets between network segments.' },
  switch:   { emoji: '🔀', analogy: 'A local distributor inside a neighbourhood — connects nearby devices.', role: 'Connects devices within the same local network segment.' },
  server:   { emoji: '🏢', analogy: 'A building that provides a specific service (office, hospital, shop).', role: 'Hosts and delivers applications or data to users.' },
  database: { emoji: '🗄️', analogy: 'A library — stores and retrieves information on request.', role: 'Persists and manages structured data for applications.' },
};

export const Chapter1: React.FC<Props> = ({ nodes, selectedNodeId }) => {
  const selected = useMemo(() => nodes.find((n) => n.id === selectedNodeId), [nodes, selectedNodeId]);
  const analogy = selected ? NODE_ANALOGIES[selected.node_type] : null;

  return (
    <GuideExplanationPanel
      chapterId={1}
      title="Understanding a Network"
      subtitle="Discover what each device does and why it matters."
    >
      <p>
        A <strong>computer network</strong> is like a city. Different buildings (devices) are connected
        by roads (cables). When you watch a video or send a message, your data travels across
        this network — just like a delivery truck drives through city roads.
      </p>

      <div className="bg-[#F8FAFC] dark:bg-[#121A2B] rounded-2xl p-4 border border-[#E2E8F0] dark:border-[#253149]">
        <p className="font-semibold text-[#171B26] dark:text-[#F5F7FF] text-xs mb-2">🖱️ Click any device in the 3D view to learn what it does</p>
        {selected && analogy ? (
          <div className="space-y-1">
            <p className="text-base text-slate-900 dark:text-[#F5F7FF]">{analogy.emoji} <strong>{selected.label ?? selected.id}</strong></p>
            <p className="text-xs font-semibold text-[#F2653A]">{selected.node_type.toUpperCase()}</p>
            <p className="text-xs text-[#475569] dark:text-[#929CB3]"><strong>Real-world analogy:</strong> {analogy.analogy}</p>
            <p className="text-xs text-[#475569] dark:text-[#929CB3]"><strong>Network role:</strong> {analogy.role}</p>
            <div className="mt-2 grid grid-cols-2 gap-1 text-[11px] font-mono-code">
              <span className="bg-[#F1F5F9] dark:bg-[#182238] dark:text-[#E2E8F0] px-2 py-1 rounded-lg">Capacity: {selected.capacity?.toFixed(0) ?? '—'}</span>
              <span className="bg-[#F1F5F9] dark:bg-[#182238] dark:text-[#E2E8F0] px-2 py-1 rounded-lg">Load: {((selected.current_load ?? 0) * 100).toFixed(0)}%</span>
            </div>
          </div>
        ) : (
          <p className="text-xs text-[#94A3B8] dark:text-[#69758E]">No device selected. Click one in the 3D scene.</p>
        )}
      </div>

      <div className="space-y-2">
        <p className="font-semibold text-[#1E293B] dark:text-[#F5F7FF] text-xs">Network devices in this lab:</p>
        {nodes.slice(0, 6).map((n) => {
          const a = NODE_ANALOGIES[n.node_type];
          return (
            <div key={n.id} className="flex items-start gap-2 text-xs text-[#475569] dark:text-[#929CB3]">
              <span className="text-base leading-none">{a?.emoji ?? '📦'}</span>
              <div>
                <span className="font-semibold text-[#1E293B] dark:text-[#F5F7FF]">{n.label ?? n.id}</span>
                <span className="ml-1 text-[#94A3B8] dark:text-[#69758E]">({n.node_type})</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="bg-[#FEF2EE] dark:bg-orange-950/30 border border-[#FECDB0] dark:border-orange-800/40 rounded-2xl p-4 text-xs text-[#7C2D12] dark:text-orange-200">
        <p className="font-semibold mb-1">💡 Key Insight</p>
        <p>
          This network has <strong>{nodes.length} devices</strong>. Each one plays a unique role.
          The entire network works together so that devices at the edges (like your laptop) can access
          services at the core (like a database server).
        </p>
      </div>
    </GuideExplanationPanel>
  );
};

