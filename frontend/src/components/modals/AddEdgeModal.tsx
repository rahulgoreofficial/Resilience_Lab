import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import type { EdgeCreateInput } from '../../types/network';

export interface AddEdgeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: EdgeCreateInput) => Promise<void>;
  nodeIds?: string[];
  isLoading?: boolean;
}

export const AddEdgeModal: React.FC<AddEdgeModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  nodeIds = [],
  isLoading = false
}) => {
  const [sourceId, setSourceId] = useState('');
  const [targetId, setTargetId] = useState('');
  const [weight, setWeight] = useState<number>(1.0);
  const [capacity, setCapacity] = useState<number>(1000);
  const [latency, setLatency] = useState<number>(2.0);
  const [reliability, setReliability] = useState<number>(0.99);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceId || !targetId) {
      setError('Both source and target vertices must be selected.');
      return;
    }
    if (sourceId === targetId) {
      setError('Self-loops are not permitted in loop-free communication topologies.');
      return;
    }
    setError(null);
    try {
      await onSubmit({
        edge_id: `${sourceId}-${targetId}`,
        source_node_id: sourceId,
        target_node_id: targetId,
        weight,
        capacity,
        latency,
        reliability
      });
      setSourceId('');
      setTargetId('');
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create link.');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Establish Communication Link"
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        {error && (
          <div className="p-3.5 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 rounded-xl text-rose-700 dark:text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-2 gap-3.5">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Source Vertex *
            </label>
            <select
              required
              value={sourceId}
              onChange={(e) => setSourceId(e.target.value)}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="">Select Endpoint A...</option>
              {nodeIds.map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Target Vertex *
            </label>
            <select
              required
              value={targetId}
              onChange={(e) => setTargetId(e.target.value)}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500 cursor-pointer"
            >
              <option value="">Select Endpoint B...</option>
              {nodeIds.filter((id) => id !== sourceId).map((id) => (
                <option key={id} value={id}>{id}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3.5">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Routing Weight (W)
            </label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={weight}
              onChange={(e) => setWeight(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Latency (ms)
            </label>
            <input
              type="number"
              step="0.5"
              min="0.1"
              value={latency}
              onChange={(e) => setLatency(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3.5">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Capacity Bandwidth (Mbps)
            </label>
            <input
              type="number"
              min="10"
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Reliability (0–1)
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="1"
              value={reliability}
              onChange={(e) => setReliability(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100 dark:border-[#253149]">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            onClick={onClose}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="brand"
            size="sm"
            isLoading={isLoading}
          >
            Establish Link
          </Button>
        </div>
      </form>
    </Modal>
  );
};
