import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import type { NodeCreateInput, NodeType } from '../../types/network';

export interface AddNodeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: NodeCreateInput) => Promise<void>;
  existingNodeIds?: string[];
  isLoading?: boolean;
}

export const AddNodeModal: React.FC<AddNodeModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  existingNodeIds = [],
  isLoading = false
}) => {
  const [nodeId, setNodeId] = useState('');
  const [nodeType, setNodeType] = useState<NodeType>('router');
  const [importance, setImportance] = useState<number>(3);
  const [capacity, setCapacity] = useState<number>(100);
  const [currentLoad, setCurrentLoad] = useState<number>(20);
  const [failureProb, setFailureProb] = useState<number>(0.01);
  const [isCritical, setIsCritical] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanId = nodeId.trim().toUpperCase();
    if (!cleanId) {
      setError('Node ID is required.');
      return;
    }
    if (existingNodeIds.includes(cleanId)) {
      setError(`Node ID "${cleanId}" already exists in active network.`);
      return;
    }
    setError(null);
    try {
      await onSubmit({
        node_id: cleanId,
        node_type: nodeType,
        importance,
        capacity,
        current_load: currentLoad,
        failure_probability: failureProb,
        is_critical: isCritical
      });
      setNodeId('');
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to add component.');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add Infrastructure Component"
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
              Node Identifier *
            </label>
            <input
              type="text"
              required
              placeholder="e.g. R3, SW2, DB1"
              value={nodeId}
              onChange={(e) => setNodeId(e.target.value)}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Component Archetype
            </label>
            <select
              value={nodeType}
              onChange={(e) => setNodeType(e.target.value as NodeType)}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none cursor-pointer"
            >
              <option value="router">Router (L3 Forwarder)</option>
              <option value="switch">Switch (L2 Fabric)</option>
              <option value="server">Server (Application Host)</option>
              <option value="database">Database (Storage Cluster)</option>
              <option value="firewall">Firewall (Security Appliance)</option>
              <option value="gateway">Gateway (Border Ingress)</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3.5">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Capacity (Mbps)
            </label>
            <input
              type="number"
              min="1"
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Initial Load (Mbps)
            </label>
            <input
              type="number"
              min="0"
              value={currentLoad}
              onChange={(e) => setCurrentLoad(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3.5">
          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Failure Probability (p)
            </label>
            <input
              type="number"
              step="0.005"
              min="0"
              max="1"
              value={failureProb}
              onChange={(e) => setFailureProb(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Importance Factor (1–5)
            </label>
            <input
              type="number"
              min="1"
              max="5"
              value={importance}
              onChange={(e) => setImportance(Number(e.target.value))}
              className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] font-mono-code focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-2 pt-1">
          <input
            type="checkbox"
            id="isCriticalCheck"
            checked={isCritical}
            onChange={(e) => setIsCritical(e.target.checked)}
            className="rounded accent-indigo-600 cursor-pointer"
          />
          <label htmlFor="isCriticalCheck" className="text-xs font-semibold text-slate-700 dark:text-[#929CB3] cursor-pointer">
            Mark as High-Priority Service (protected SLA)
          </label>
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
            Add Component
          </Button>
        </div>
      </form>
    </Modal>
  );
};
