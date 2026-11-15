import React from 'react';
import { 
  X, 
  Server, 
  ShieldAlert, 
  Play, 
  Trash2
} from 'lucide-react';
import type { CytoscapeNodeData } from '../../types/network';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export interface NodeInspectorProps {
  node: CytoscapeNodeData | null;
  onClose: () => void;
  onSimulateFailure?: (nodeId: string) => void;
  onDeleteNode?: (nodeId: string) => void;
  isArticulationPoint?: boolean;
  connectedNeighbours?: string[];
}

export const NodeInspector: React.FC<NodeInspectorProps> = ({
  node,
  onClose,
  onSimulateFailure,
  onDeleteNode,
  isArticulationPoint = false,
  connectedNeighbours = []
}) => {
  if (!node) return null;

  return (
    <div className="w-88 bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border-l border-slate-200/90 dark:border-[#253149] h-full flex flex-col shadow-2xl z-20 animate-in slide-in-from-right duration-200 text-[#171923] dark:text-[#F5F7FF] transition-colors">
      {/* Header */}
      <div className="p-5 border-b border-slate-100 dark:border-[#253149] flex items-center justify-between bg-slate-50/60 dark:bg-[#121A2B]/70">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-orange-50 dark:bg-rose-950/40 border border-orange-200/80 dark:border-rose-800/60 text-[#FF784F]">
            <Server className="w-4 h-4" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-[#171923] dark:text-[#F5F7FF] tracking-tight">Component Inspector</h3>
            <span className="text-[10px] text-slate-400 dark:text-[#69758E] font-mono-code">NODE PROPERTIES</span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-[#F5F7FF] hover:bg-slate-200/60 dark:hover:bg-[#182238] rounded-full cursor-pointer transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Content */}
      <div className="p-5 flex-1 overflow-y-auto space-y-5 text-xs">
        {/* Identity & Status */}
        <div className="p-4 bg-slate-50/90 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl flex items-center justify-between">
          <div>
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Node Identifier</span>
            <div className="text-xl font-black font-mono-code text-slate-900 dark:text-[#F5F7FF]">{node.id}</div>
          </div>
          <Badge variant="cyan" size="md">
            {node.node_type}
          </Badge>
        </div>

        {/* SPOF Alert Banner */}
        {isArticulationPoint && (
          <div className="p-4 bg-rose-50/90 dark:bg-rose-950/30 border border-rose-200/90 dark:border-rose-500/40 rounded-2xl flex items-start gap-3 shadow-2xs">
            <ShieldAlert className="w-5 h-5 text-[#FF784F] shrink-0 mt-0.5" />
            <div>
              <div className="font-bold text-[#FF784F] text-xs">Single Point of Failure (SPOF)</div>
              <p className="text-[11px] text-rose-950/80 dark:text-rose-200/90 mt-1 leading-relaxed">
                This node is a mathematical cut-vertex. Removing it will partition the communication network into isolated subgraphs.
              </p>
            </div>
          </div>
        )}

        {/* Technical Attributes Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Capacity</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{node.capacity} Mbps</div>
          </div>
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Current Load</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{node.current_load} Mbps</div>
          </div>
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Importance</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">I = {node.importance}</div>
          </div>
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Failure Prob (p)</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{node.failure_probability}</div>
          </div>
        </div>

        {/* Connected Neighbours */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[11px] text-slate-600 dark:text-[#929CB3] uppercase font-mono-code font-semibold">
              Adjacency Degree: {connectedNeighbours.length}
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl min-h-[50px]">
            {connectedNeighbours.length > 0 ? (
              connectedNeighbours.map((nbr) => (
                <span
                  key={nbr}
                  className="px-2.5 py-1 bg-white dark:bg-[#182238] border border-slate-200 dark:border-[#253149] rounded-lg font-mono-code text-[11px] font-semibold text-slate-700 dark:text-[#F5F7FF] shadow-2xs"
                >
                  {nbr}
                </span>
              ))
            ) : (
              <span className="text-slate-400 dark:text-[#69758E] text-xs italic">Isolated component</span>
            )}
          </div>
        </div>
      </div>

      {/* Footer Quick Actions */}
      <div className="p-4 border-t border-slate-100 dark:border-[#253149] bg-slate-50/80 dark:bg-[#121A2B]/80 flex items-center gap-2">
        {onSimulateFailure && (
          <Button
            size="sm"
            variant="danger"
            className="flex-1"
            icon={<Play className="w-3.5 h-3.5" />}
            onClick={() => onSimulateFailure(node.id)}
          >
            Simulate Outage
          </Button>
        )}
        {onDeleteNode && (
          <Button
            size="sm"
            variant="outline"
            icon={<Trash2 className="w-3.5 h-3.5 text-rose-500" />}
            onClick={() => onDeleteNode(node.id)}
            title="Delete node from database"
          />
        )}
      </div>
    </div>
  );
};
