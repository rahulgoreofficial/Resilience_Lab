import React, { useState } from 'react';
import { 
  Search, 
  Layers, 
  Route, 
  X,
  Maximize2
} from 'lucide-react';
import { Button } from '../common/Button';

export interface GraphControlsProps {
  layoutName: 'cose' | 'concentric' | 'circle' | 'breadthfirst' | 'grid';
  onLayoutChange: (layout: 'cose' | 'concentric' | 'circle' | 'breadthfirst' | 'grid') => void;
  nodeIds: string[];
  onSearchNode: (nodeId: string) => void;
  onFindPath: (source: string, target: string) => void;
  onClearPath: () => void;
  hasActivePath: boolean;
  onFitScreen?: () => void;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  layoutName,
  onLayoutChange,
  nodeIds,
  onSearchNode,
  onFindPath,
  onClearPath,
  hasActivePath,
  onFitScreen
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sourceNode, setSourceNode] = useState('');
  const [targetNode, setTargetNode] = useState('');
  const [showPathFinder, setShowPathFinder] = useState(false);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      onSearchNode(searchQuery.trim());
    }
  };

  const handlePathSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (sourceNode && targetNode && sourceNode !== targetNode) {
      onFindPath(sourceNode, targetNode);
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 bg-white/90 dark:bg-[#0D1220]/90 backdrop-blur-md border border-slate-200/80 dark:border-[#253149] rounded-2xl shadow-xs text-xs text-[#171923] dark:text-[#F5F7FF] transition-colors">
      {/* Node Search Bar */}
      <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 min-w-[220px]">
        <div className="relative flex-1">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Find vertex ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 dark:bg-[#121A2B] border border-slate-200/90 dark:border-[#253149] rounded-xl focus:outline-none focus:border-indigo-500 dark:focus:border-cyan-400 font-mono-code text-slate-900 dark:text-[#F5F7FF] transition-colors"
          />
        </div>
        <Button size="sm" variant="secondary" type="submit">
          Locate
        </Button>
      </form>

      {/* Path Finder & Layout Switcher */}
      <div className="flex flex-wrap items-center gap-2.5">
        <Button
          size="sm"
          variant={showPathFinder ? 'brand' : 'outline'}
          icon={<Route className="w-3.5 h-3.5" />}
          onClick={() => setShowPathFinder(!showPathFinder)}
        >
          Shortest Path
        </Button>

        {hasActivePath && (
          <Button
            size="sm"
            variant="ghost"
            icon={<X className="w-3.5 h-3.5 text-rose-500" />}
            onClick={onClearPath}
          >
            Clear Path
          </Button>
        )}

        {onFitScreen && (
          <Button
            size="sm"
            variant="outline"
            icon={<Maximize2 className="w-3.5 h-3.5 text-slate-600 dark:text-slate-300" />}
            onClick={onFitScreen}
            title="Fit graph to canvas"
          >
            Fit
          </Button>
        )}

        {/* Layout Switcher */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-200/80 dark:border-[#253149]">
          <Layers className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
          <span className="text-[11px] text-slate-500 dark:text-[#929CB3] font-mono-code uppercase hidden sm:inline font-semibold">Layout:</span>
          <select
            value={layoutName}
            onChange={(e) => onLayoutChange(e.target.value as any)}
            className="text-xs bg-slate-50 dark:bg-[#121A2B] border border-slate-200/90 dark:border-[#253149] rounded-xl px-2.5 py-1.5 font-mono-code text-slate-800 dark:text-[#F5F7FF] focus:outline-none cursor-pointer"
          >
            <option value="cose">Force-Directed (Cose)</option>
            <option value="concentric">Concentric Hierarchy</option>
            <option value="circle">Circular Ring</option>
            <option value="breadthfirst">Breadth-First Tree</option>
            <option value="grid">Orthogonal Grid</option>
          </select>
        </div>
      </div>

      {/* Path Finder Popover */}
      {showPathFinder && (
        <form onSubmit={handlePathSubmit} className="w-full flex flex-wrap items-center gap-2 pt-3 border-t border-slate-100 dark:border-[#253149] animate-in fade-in duration-150">
          <span className="text-[11px] font-semibold text-slate-600 dark:text-slate-300 font-mono-code uppercase">Dijkstra Routing:</span>
          <select
            value={sourceNode}
            onChange={(e) => setSourceNode(e.target.value)}
            className="bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-2.5 py-1 text-xs font-mono-code text-slate-800 dark:text-[#F5F7FF] focus:outline-none"
          >
            <option value="">Select Source Node...</option>
            {nodeIds.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          <span className="text-slate-400 font-mono-code">&rarr;</span>
          <select
            value={targetNode}
            onChange={(e) => setTargetNode(e.target.value)}
            className="bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-2.5 py-1 text-xs font-mono-code text-slate-800 dark:text-[#F5F7FF] focus:outline-none"
          >
            <option value="">Select Destination...</option>
            {nodeIds.map((id) => (
              <option key={id} value={id}>{id}</option>
            ))}
          </select>
          <Button size="sm" variant="brand" type="submit" disabled={!sourceNode || !targetNode || sourceNode === targetNode}>
            Trace Shortest Path
          </Button>
        </form>
      )}
    </div>
  );
};
