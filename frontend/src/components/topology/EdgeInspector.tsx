import React from 'react';
import { 
  X, 
  GitFork, 
  ShieldAlert, 
  Play, 
  Trash2
} from 'lucide-react';
import type { CytoscapeEdgeData } from '../../types/network';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';

export interface EdgeInspectorProps {
  edge: CytoscapeEdgeData | null;
  onClose: () => void;
  onSimulateSeverance?: (source: string, target: string) => void;
  onDeleteEdge?: (edgeId: string) => void;
  isBridge?: boolean;
}

export const EdgeInspector: React.FC<EdgeInspectorProps> = ({
  edge,
  onClose,
  onSimulateSeverance,
  onDeleteEdge,
  isBridge = false
}) => {
  if (!edge) return null;

  return (
    <div className="w-88 bg-white/95 dark:bg-[#0D1220]/95 backdrop-blur-md border-l border-slate-200/90 dark:border-[#253149] h-full flex flex-col shadow-2xl z-20 animate-in slide-in-from-right duration-200 text-[#171923] dark:text-[#F5F7FF] transition-colors">
      {/* Header */}
      <div className="p-5 border-b border-slate-100 dark:border-[#253149] flex items-center justify-between bg-slate-50/60 dark:bg-[#121A2B]/70">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-cyan-50 dark:bg-cyan-950/40 border border-cyan-200/80 dark:border-cyan-800/60 text-[#22D3EE]">
            <GitFork className="w-4 h-4 text-cyan-600 dark:text-[#22D3EE]" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-[#171923] dark:text-[#F5F7FF] tracking-tight">Link Inspector</h3>
            <span className="text-[10px] text-slate-400 dark:text-[#69758E] font-mono-code">COMMUNICATION EDGE</span>
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
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Link Identifier</span>
            <div className="text-base font-black font-mono-code text-slate-900 dark:text-[#F5F7FF] truncate max-w-[170px]">{edge.id}</div>
          </div>
          <Badge variant={isBridge ? 'critical' : 'cyan'} size="md">
            {isBridge ? 'BRIDGE' : 'ACTIVE LINK'}
          </Badge>
        </div>

        {/* Bridge Alert Banner */}
        {isBridge && (
          <div className="p-4 bg-rose-50/90 dark:bg-rose-950/30 border border-rose-200/90 dark:border-rose-500/40 rounded-2xl flex items-start gap-3 shadow-2xs">
            <ShieldAlert className="w-5 h-5 text-[#FF784F] shrink-0 mt-0.5" />
            <div>
              <div className="font-bold text-[#FF784F] text-xs">Critical Network Bridge</div>
              <p className="text-[11px] text-rose-950/80 dark:text-rose-200/90 mt-1 leading-relaxed">
                This communication link is a mathematical Cut-Edge. Severing it increases graph component count and severs subnetworks.
              </p>
            </div>
          </div>
        )}

        {/* Endpoints Diagram */}
        <div className="p-4 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-2xl flex items-center justify-between font-mono-code">
          <span className="font-bold text-slate-900 dark:text-[#F5F7FF] bg-white dark:bg-[#182238] px-3 py-1.5 rounded-xl border border-slate-200 dark:border-[#253149] shadow-2xs">
            {edge.source}
          </span>
          <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase tracking-wider font-semibold">
            &larr;&rarr; Undirected
          </span>
          <span className="font-bold text-slate-900 dark:text-[#F5F7FF] bg-white dark:bg-[#182238] px-3 py-1.5 rounded-xl border border-slate-200 dark:border-[#253149] shadow-2xs">
            {edge.target}
          </span>
        </div>

        {/* Technical Attributes Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Weight</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">W = {edge.weight}</div>
          </div>
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Latency</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{edge.latency} ms</div>
          </div>
          <div className="p-3 bg-slate-50/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Bandwidth</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{edge.capacity} Gbps</div>
          </div>
          <div className="p-3 bg-slate-50/80 dark:bg-[#121A2B]/80 border border-slate-200/80 dark:border-[#253149] rounded-xl">
            <span className="text-[10px] text-slate-500 dark:text-[#929CB3] uppercase font-mono-code font-semibold">Reliability</span>
            <div className="text-base font-bold font-mono-code text-slate-900 dark:text-[#F5F7FF] mt-0.5">{edge.reliability ?? 0.99}</div>
          </div>
        </div>
      </div>

      {/* Footer Quick Actions */}
      <div className="p-4 border-t border-slate-100 dark:border-[#253149] bg-slate-50/80 dark:bg-[#121A2B]/80 flex items-center gap-2">
        {onSimulateSeverance && (
          <Button
            size="sm"
            variant="danger"
            className="flex-1"
            icon={<Play className="w-3.5 h-3.5" />}
            onClick={() => onSimulateSeverance(edge.source, edge.target)}
          >
            Sever Cable Link
          </Button>
        )}
        {onDeleteEdge && (
          <Button
            size="sm"
            variant="outline"
            icon={<Trash2 className="w-3.5 h-3.5 text-rose-500" />}
            onClick={() => onDeleteEdge(edge.id)}
            title="Delete link from database"
          />
        )}
      </div>
    </div>
  );
};
