import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export interface ImportNetworkModalProps {
  isOpen: boolean;
  onClose: () => void;
  onImport: (payload: { name: string; description?: string; network_type?: string; data: Record<string, unknown> }) => Promise<void>;
  isLoading?: boolean;
}

const SAMPLE_JSON = {
  name: "Campus High-Speed Mesh",
  description: "Dual-switch resilient campus backbone with server cluster.",
  network_type: "CAMPUS_BACKBONE",
  nodes: [
    { id: "core_r1", type: "router", capacity: 1000, load: 120, importance: 1.0 },
    { id: "core_r2", type: "router", capacity: 1000, load: 110, importance: 1.0 },
    { id: "dist_sw1", type: "switch", capacity: 500, load: 80, importance: 0.8 },
    { id: "dist_sw2", type: "switch", capacity: 500, load: 85, importance: 0.8 },
    { id: "app_srv1", type: "server", capacity: 300, load: 45, importance: 0.7 },
    { id: "db_cluster", type: "database", capacity: 600, load: 150, importance: 0.95 }
  ],
  edges: [
    { source: "core_r1", target: "core_r2", weight: 1.0, bandwidth: 10000 },
    { source: "core_r1", target: "dist_sw1", weight: 1.5, bandwidth: 4000 },
    { source: "core_r2", target: "dist_sw2", weight: 1.5, bandwidth: 4000 },
    { source: "dist_sw1", target: "dist_sw2", weight: 2.0, bandwidth: 4000 },
    { source: "dist_sw1", target: "app_srv1", weight: 1.0, bandwidth: 1000 },
    { source: "dist_sw2", target: "app_srv1", weight: 1.2, bandwidth: 1000 },
    { source: "app_srv1", target: "db_cluster", weight: 0.8, bandwidth: 2000 }
  ]
};

export const ImportNetworkModal: React.FC<ImportNetworkModalProps> = ({
  isOpen,
  onClose,
  onImport,
  isLoading = false
}) => {
  const [jsonText, setJsonText] = useState('');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [networkType, setNetworkType] = useState('COMMUNICATION_NETWORK');
  const [error, setError] = useState<string | null>(null);
  const [parsedStats, setParsedStats] = useState<{ nodeCount: number; edgeCount: number } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const parseAndValidate = (text: string) => {
    try {
      if (!text.trim()) {
        setParsedStats(null);
        setError(null);
        return;
      }
      const obj = JSON.parse(text);
      if (typeof obj !== 'object' || obj === null) {
        throw new Error('JSON root must be an object.');
      }

      let nodes = 0;
      let edges = 0;

      if (obj.elements && typeof obj.elements === 'object') {
        nodes = Array.isArray(obj.elements.nodes) ? obj.elements.nodes.length : 0;
        edges = Array.isArray(obj.elements.edges) ? obj.elements.edges.length : 0;
      } else {
        nodes = Array.isArray(obj.nodes) ? obj.nodes.length : 0;
        edges = Array.isArray(obj.edges) ? obj.edges.length : (Array.isArray(obj.links) ? obj.links.length : 0);
      }

      if (nodes === 0 && edges === 0) {
        throw new Error('No nodes or edges detected. Ensure JSON contains "nodes" and "edges" arrays.');
      }

      setParsedStats({ nodeCount: nodes, edgeCount: edges });
      setError(null);

      // Auto-fill metadata if present in JSON and user hasn't typed
      if (obj.name && !name) {
        setName(obj.name);
      }
      if (obj.description && !description) {
        setDescription(obj.description);
      }
      if (obj.network_type) {
        setNetworkType(obj.network_type);
      }
    } catch (err: unknown) {
      setParsedStats(null);
      setError(err instanceof Error ? err.message : 'Invalid JSON format.');
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setJsonText(val);
    parseAndValidate(val);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!name) {
      setName(file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, ' '));
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setJsonText(content);
      parseAndValidate(content);
    };
    reader.readAsText(file);
  };

  const handleLoadSample = () => {
    const sampleStr = JSON.stringify(SAMPLE_JSON, null, 2);
    setJsonText(sampleStr);
    setName(SAMPLE_JSON.name);
    setDescription(SAMPLE_JSON.description);
    setNetworkType(SAMPLE_JSON.network_type);
    parseAndValidate(sampleStr);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!jsonText.trim()) {
      setError('Please provide JSON graph data or upload a file.');
      return;
    }

    try {
      const dataObj = JSON.parse(jsonText);
      const networkName = (name.trim() || dataObj.name || 'Imported Network').substring(0, 128);

      setError(null);
      await onImport({
        name: networkName,
        description: description.trim() || dataObj.description || undefined,
        network_type: networkType || dataObj.network_type || 'COMMUNICATION_NETWORK',
        data: dataObj
      });

      // Reset and close
      setJsonText('');
      setName('');
      setDescription('');
      setParsedStats(null);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to import network JSON.');
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Import Network Topology (JSON)"
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit} className="space-y-4 text-xs">
        {error && (
          <div className="p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50 rounded-xl text-rose-700 dark:text-rose-300 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 dark:text-rose-400" />
            <span className="font-medium">{error}</span>
          </div>
        )}

        {parsedStats && (
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/50 rounded-xl text-emerald-800 dark:text-emerald-300 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 shrink-0" />
              <span className="font-semibold">Valid Graph Structure Detected</span>
            </div>
            <div className="flex items-center gap-3 font-mono text-[11px]">
              <span className="bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 px-2 py-0.5 rounded font-bold">{parsedStats.nodeCount} Nodes</span>
              <span className="bg-emerald-100 dark:bg-emerald-900/60 text-emerald-800 dark:text-emerald-200 px-2 py-0.5 rounded font-bold">{parsedStats.edgeCount} Edges</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
          <div>
            <label className="block text-slate-700 dark:text-[#929CB3] font-semibold mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Network Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              className="w-full px-3.5 py-2 border border-slate-200 dark:border-[#253149] rounded-xl focus:outline-none focus:border-indigo-500 text-slate-900 dark:text-[#F5F7FF] bg-slate-50 dark:bg-[#121A2B] font-mono-code transition-colors"
              placeholder="e.g., Enterprise Core Backbone"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="block text-slate-700 dark:text-[#929CB3] font-semibold mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
              Network Classification
            </label>
            <select
              className="w-full px-3.5 py-2 border border-slate-200 dark:border-[#253149] rounded-xl focus:outline-none focus:border-indigo-500 text-slate-900 dark:text-[#F5F7FF] bg-slate-50 dark:bg-[#121A2B] font-mono-code cursor-pointer"
              value={networkType}
              onChange={(e) => setNetworkType(e.target.value)}
            >
              <option value="COMMUNICATION_NETWORK">Communication Network</option>
              <option value="ENTERPRISE_DATACENTER">Enterprise Datacenter</option>
              <option value="CAMPUS_BACKBONE">Campus Backbone</option>
              <option value="REGIONAL_WAN">Regional WAN / Metro Ring</option>
              <option value="CUSTOM">Custom Mesh</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-slate-700 dark:text-[#929CB3] font-semibold mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
            Description <span className="text-slate-400 dark:text-[#69758E] font-normal">(optional)</span>
          </label>
          <input
            type="text"
            className="w-full px-3.5 py-2 border border-slate-200 dark:border-[#253149] rounded-xl focus:outline-none focus:border-indigo-500 text-slate-900 dark:text-[#F5F7FF] bg-slate-50 dark:bg-[#121A2B] transition-colors"
            placeholder="Brief topology background or operational notes..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        {/* Upload Zone & Load Sample Actions */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              accept=".json,application/json"
              className="hidden"
              onChange={handleFileUpload}
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              icon={<Upload className="w-3.5 h-3.5 text-indigo-600" />}
              onClick={() => fileInputRef.current?.click()}
            >
              Upload .json File
            </Button>

            <Button
              type="button"
              variant="secondary"
              size="sm"
              icon={<Sparkles className="w-3.5 h-3.5 text-amber-500" />}
              onClick={handleLoadSample}
            >
              Load Sample Mesh JSON
            </Button>
          </div>

          <span className="text-slate-400 dark:text-[#69758E] text-[11px] flex items-center gap-1 font-mono-code">
            <FileText className="w-3 h-3" /> Supports Cytoscape &amp; Graph JSON
          </span>
        </div>

        {/* JSON Code Area */}
        <div>
          <label className="block text-slate-700 dark:text-[#929CB3] font-semibold mb-1.5 font-mono-code uppercase tracking-wider text-[11px]">
            JSON Topology Definition
          </label>
          <textarea
            className="w-full h-44 px-3.5 py-2.5 font-mono-code text-[11px] border border-slate-200 dark:border-[#253149] rounded-2xl focus:outline-none focus:border-indigo-500 text-slate-800 dark:text-[#F5F7FF] bg-slate-50 dark:bg-[#121A2B] leading-relaxed resize-none transition-colors"
            placeholder='{&#10;  "nodes": [&#10;    { "id": "r1", "type": "router" },&#10;    { "id": "s1", "type": "server" }&#10;  ],&#10;  "edges": [&#10;    { "source": "r1", "target": "s1", "weight": 1.0 }&#10;  ]&#10;}'
            value={jsonText}
            onChange={handleTextChange}
            required
          />
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-3 border-t border-slate-100 dark:border-[#253149]">
          <Button type="button" variant="secondary" size="sm" onClick={onClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="brand"
            size="sm"
            isLoading={isLoading}
            disabled={!jsonText.trim() || !!error}
            icon={<Upload className="w-3.5 h-3.5 text-white" />}
          >
            Import Topology
          </Button>
        </div>
      </form>
    </Modal>
  );
};

