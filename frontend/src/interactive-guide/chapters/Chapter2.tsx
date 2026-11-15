/**
 * Chapter 2 — Understanding Connections (Graph Theory Intro)
 */

import React, { useMemo } from 'react';
import { GuideExplanationPanel } from '../GuideExplanationPanel';
import type { CytoscapeNodeData, CytoscapeEdgeData } from '../../types/network';

interface Props {
  nodes: CytoscapeNodeData[];
  edges: CytoscapeEdgeData[];
  selectedEdgeId: string | null;
  selectedNodeId: string | null;
}

export const Chapter2: React.FC<Props> = ({ nodes, edges, selectedEdgeId, selectedNodeId }) => {
  const degrees = useMemo(() => {
    const d = new Map<string, number>();
    for (const e of edges) {
      d.set(e.source, (d.get(e.source) ?? 0) + 1);
      d.set(e.target, (d.get(e.target) ?? 0) + 1);
    }
    return d;
  }, [edges]);

  const selectedEdge = useMemo(() => edges.find((e) => e.id === selectedEdgeId), [edges, selectedEdgeId]);
  const selectedNode = useMemo(() => nodes.find((n) => n.id === selectedNodeId), [nodes, selectedNodeId]);
  const adjList = useMemo(() => {
    const a = new Map<string, string[]>();
    for (const e of edges) {
      if (!a.has(e.source)) a.set(e.source, []);
      if (!a.has(e.target)) a.set(e.target, []);
      a.get(e.source)!.push(e.target);
      a.get(e.target)!.push(e.source);
    }
    return a;
  }, [edges]);

  return (
    <GuideExplanationPanel
      chapterId={2}
      title="Understanding Connections"
      subtitle="How graph theory models network links."
    >
      <p>
        In <strong>Graph Theory</strong>, we represent a network as:
      </p>

      <div className="bg-[#0B1120] text-[#22D3EE] rounded-xl p-3 font-mono text-sm text-center border border-[#1E293B]">
        G = (V, E)
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-[#EFF6FF] dark:bg-blue-950/30 border border-[#BFDBFE] dark:border-blue-900/40 rounded-xl p-3">
          <p className="font-bold text-[#1D4ED8] dark:text-[#4F8CFF]">V = Vertices (Nodes)</p>
          <p className="text-[#475569] dark:text-[#929CB3] mt-0.5">The set of all <strong>{nodes.length}</strong> network devices.</p>
        </div>
        <div className="bg-[#F0FDF4] dark:bg-emerald-950/30 border border-[#BBF7D0] dark:border-emerald-900/40 rounded-xl p-3">
          <p className="font-bold text-[#15803D] dark:text-emerald-400">E = Edges (Links)</p>
          <p className="text-[#475569] dark:text-[#929CB3] mt-0.5">The set of all <strong>{edges.length}</strong> connections.</p>
        </div>
      </div>

      {/* Live vertex set */}
      <div className="space-y-1">
        <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF]">V = {`{${nodes.map(n => n.id).join(', ')}`}{'}'}</p>
        <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF]">E = {`{${edges.slice(0,3).map(e => `(${e.source}, ${e.target})`).join(', ')}...`}{'}'}</p>
      </div>

      {/* Selected node info */}
      {selectedNode && (
        <div className="bg-[#F0F9FF] dark:bg-sky-950/30 border border-[#BAE6FD] dark:border-sky-900/40 rounded-xl p-3 text-xs">
          <p className="font-semibold text-[#0369A1] dark:text-cyan-400">Node: {selectedNode.id}</p>
          <p className="text-[#475569] dark:text-[#929CB3]">Degree: <strong>{degrees.get(selectedNode.id) ?? 0}</strong> (number of connections)</p>
          <p className="text-[#475569] dark:text-[#929CB3]">Neighbours: {(adjList.get(selectedNode.id) ?? []).join(', ') || 'none'}</p>
        </div>
      )}

      {/* Selected edge info */}
      {selectedEdge && (
        <div className="bg-[#F5F3FF] dark:bg-purple-950/30 border border-[#DDD6FE] dark:border-purple-900/40 rounded-xl p-3 text-xs">
          <p className="font-semibold text-[#6D28D9] dark:text-[#9B7BFF]">Edge: {selectedEdge.id}</p>
          <p className="text-[#475569] dark:text-[#929CB3]">Source: <strong>{selectedEdge.source}</strong></p>
          <p className="text-[#475569] dark:text-[#929CB3]">Target: <strong>{selectedEdge.target}</strong></p>
          <p className="text-[#475569] dark:text-[#929CB3]">Weight: {selectedEdge.weight} | Latency: {selectedEdge.latency}ms | Capacity: {selectedEdge.capacity} Mbps</p>
        </div>
      )}

      {/* Adjacency list */}
      <div>
        <p className="text-xs font-semibold text-[#1E293B] dark:text-[#F5F7FF] mb-2">Adjacency List (click a node to highlight it):</p>
        <div className="space-y-1 font-mono text-[11px]">
          {nodes.slice(0, 5).map((n) => (
            <div key={n.id} className="flex gap-2 text-[#475569] dark:text-[#929CB3]">
              <span className="text-[#F2653A] font-bold w-12 shrink-0">{n.id}:</span>
              <span>[{(adjList.get(n.id) ?? []).join(', ')}]</span>
            </div>
          ))}
          {nodes.length > 5 && <p className="text-[#94A3B8] dark:text-[#69758E]">...and {nodes.length - 5} more nodes</p>}
        </div>
      </div>

      <div className="bg-[#FEF2EE] dark:bg-orange-950/30 border border-[#FECDB0] dark:border-orange-800/40 rounded-xl p-3 text-xs text-[#7C2D12] dark:text-orange-200">
        <p className="font-semibold mb-1">💡 Key Insight</p>
        <p>The <strong>degree</strong> of a node tells us how many connections it has.
          Highly-connected nodes are often more important — removing them affects more of the network.
        </p>
      </div>
    </GuideExplanationPanel>
  );
};

