import React, { useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';
import type { NetworkCreateInput } from '../../types/network';

export interface CreateNetworkModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (input: NetworkCreateInput) => Promise<void>;
  isLoading?: boolean;
}

export const CreateNetworkModal: React.FC<CreateNetworkModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  isLoading = false
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [networkType, setNetworkType] = useState('undirected');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Network name is required.');
      return;
    }
    setError(null);
    try {
      await onSubmit({
        name: name.trim(),
        description: description.trim() || undefined,
        network_type: networkType
      });
      setName('');
      setDescription('');
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to create network.');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Create Infrastructure Network"
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        {error && (
          <div className="p-3.5 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 rounded-xl text-rose-700 dark:text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
            Network Name *
          </label>
          <input
            type="text"
            required
            placeholder="e.g. Enterprise DC Spine-Leaf"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] focus:outline-none focus:border-indigo-500 font-mono-code transition-colors"
          />
        </div>

        <div>
          <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
            Description
          </label>
          <textarea
            rows={3}
            placeholder="Topology description and design notes..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>

        <div>
          <label className="block font-semibold text-slate-700 dark:text-[#929CB3] mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
            Graph Topology Model
          </label>
          <select
            value={networkType}
            onChange={(e) => setNetworkType(e.target.value)}
            className="w-full bg-slate-50 dark:bg-[#121A2B] border border-slate-200 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-slate-900 dark:text-[#F5F7FF] focus:outline-none cursor-pointer font-mono-code"
          >
            <option value="undirected">Undirected (Symmetric physical communication links)</option>
            <option value="directed">Directed (Asymmetric dependency graph)</option>
          </select>
          <p className="text-[11px] text-slate-400 dark:text-[#69758E] mt-1">
            Undirected models physical bi-directional ethernet or fiber optics trunks.
          </p>
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
            Create Network
          </Button>
        </div>
      </form>
    </Modal>
  );
};
