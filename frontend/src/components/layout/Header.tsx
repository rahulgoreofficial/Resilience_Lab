import React from 'react';
import { 
  Network as NetworkIcon, 
  ChevronDown, 
  Plus, 
  Upload, 
  Database, 
  Activity, 
  CheckCircle2, 
  AlertCircle, 
  GraduationCap, 
  Sparkles 
} from 'lucide-react';
import type { Network } from '../../types/network';
import type { SystemHealth, DatabaseHealth } from '../../types/api';
import { Button } from '../common/Button';
import { ThemeSwitcher } from '../common/ThemeSwitcher';

export interface HeaderProps {
  networks: Network[];
  selectedNetwork: Network | null;
  onSelectNetwork: (network: Network) => void;
  onCreateNetworkClick: () => void;
  onImportNetworkClick?: () => void;
  onNavigateToGuide?: () => void;
  systemHealth: SystemHealth | null;
  dbHealth: DatabaseHealth | null;
  isSimulating?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  networks,
  selectedNetwork,
  onSelectNetwork,
  onCreateNetworkClick,
  onImportNetworkClick,
  onNavigateToGuide,
  systemHealth,
  dbHealth,
  isSimulating = false
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-white/85 dark:bg-[#080B14]/85 backdrop-blur-md border-b border-slate-200/80 dark:border-[#253149] shadow-[0_1px_8px_rgba(0,0,0,0.03)] dark:shadow-[0_4px_20px_rgba(0,0,0,0.4)] transition-colors">
      <div className="w-full px-4 sm:px-6 lg:px-8 h-18 flex items-center justify-between gap-4">
        {/* Brand & Wordmark */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#080B14] to-[#121A2B] border border-slate-700/80 dark:border-[#253149] flex items-center justify-center text-white shadow-md relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-tr from-[#6366F1]/20 via-transparent to-[#22D3EE]/20 opacity-0 group-hover:opacity-100 transition-opacity" />
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" className="text-[#22D3EE]">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v4" />
              <path d="M12 18v4" />
              <path d="M4.93 4.93l2.83 2.83" />
              <path d="M16.24 16.24l2.83 2.83" />
              <path d="M2 12h4" />
              <path d="M18 12h4" />
              <path d="M4.93 19.07l2.83-2.83" />
              <path d="M16.24 7.76l2.83-2.83" />
            </svg>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold tracking-tight text-xl text-[#171923] dark:text-[#F5F7FF]">
                RESILIENCE<span className="text-gradient-orange">LAB</span>
              </span>
              <span className="hidden sm:inline-flex items-center gap-1 text-[10px] uppercase font-mono-code bg-slate-100 dark:bg-[#182238] text-slate-700 dark:text-cyan-400 px-2 py-0.5 rounded-full border border-slate-200/90 dark:border-[#253149] font-medium">
                <Sparkles className="w-2.5 h-2.5 text-[#3B82F6] dark:text-[#22D3EE]" />
                INTELLIGENCE
              </span>
            </div>
            <p className="text-[12px] text-[#737B8C] dark:text-[#929CB3] hidden md:block tracking-tight -mt-0.5 font-medium">
              Infrastructure Intelligence & Network Resilience
            </p>
          </div>
        </div>

        {/* Network Selector, Theme Switcher & Actions */}
        <div className="flex items-center gap-2.5 sm:gap-3">
          {/* Network Picker */}
          <div className="relative">
            {networks.length > 0 ? (
              <div className="flex items-center gap-2 bg-slate-50/90 dark:bg-[#0D1220] border border-slate-200/90 dark:border-[#253149] rounded-xl px-3.5 py-2 text-xs text-[#171923] dark:text-[#F5F7FF] shadow-xs hover:border-slate-300 dark:hover:border-[#4F8CFF]/50 transition-all">
                <NetworkIcon className="w-4 h-4 text-[#3B82F6] dark:text-[#22D3EE] shrink-0" />
                <select
                  value={selectedNetwork?.id || ''}
                  onChange={(e) => {
                    const found = networks.find((n) => n.id === e.target.value);
                    if (found) onSelectNetwork(found);
                  }}
                  className="bg-transparent font-medium text-xs text-[#171923] dark:text-[#F5F7FF] focus:outline-none cursor-pointer pr-4 appearance-none font-mono-code"
                >
                  {networks.map((net) => (
                    <option key={net.id} value={net.id} className="dark:bg-[#0D1220] dark:text-[#F5F7FF]">
                      {net.name} ({net.node_count}N · {net.edge_count}E)
                    </option>
                  ))}
                </select>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400 pointer-events-none -ml-3" />
              </div>
            ) : (
              <span className="text-xs text-slate-400 italic">No networks loaded</span>
            )}
          </div>

          {/* Action Buttons */}
          <div className="hidden sm:flex items-center gap-2">
            {onNavigateToGuide && (
              <Button
                size="sm"
                variant="brand"
                icon={<GraduationCap className="w-3.5 h-3.5 text-white" />}
                onClick={onNavigateToGuide}
                className="font-medium"
              >
                3D Network Lab
              </Button>
            )}

            {onImportNetworkClick && (
              <Button
                size="sm"
                variant="outline"
                icon={<Upload className="w-3.5 h-3.5 text-indigo-600 dark:text-cyan-400" />}
                onClick={onImportNetworkClick}
              >
                Import JSON
              </Button>
            )}

            <Button
              size="sm"
              variant="secondary"
              icon={<Plus className="w-3.5 h-3.5 text-slate-700 dark:text-slate-200" />}
              onClick={onCreateNetworkClick}
            >
              New Network
            </Button>
          </div>

          {/* Theme Switcher */}
          <ThemeSwitcher size="sm" />

          {/* Telemetry Status Badges */}
          <div className="hidden lg:flex items-center gap-2.5 pl-3 border-l border-slate-200/80 dark:border-[#253149]">
            {/* API Engine Health */}
            <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-[#929CB3] bg-slate-50 dark:bg-[#121A2B] px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-[#253149]">
              <span className={`w-2 h-2 rounded-full ${systemHealth?.status === 'degraded' ? 'bg-amber-500' : 'bg-emerald-500 dark:bg-[#20D6A0]'} animate-pulse`} />
              <span className="font-mono-code text-[11px] font-medium">
                {systemHealth?.status ? systemHealth.status.toUpperCase() : 'API ONLINE'}
              </span>
            </div>

            {/* Database indicator */}
            <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-[#929CB3] bg-slate-50 dark:bg-[#121A2B] px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-[#253149]">
              <Database className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
              <span className="font-mono-code text-[11px] font-medium">
                {dbHealth?.dialect === 'postgresql' ? 'POSTGRESQL' : 'SQLITE STORAGE'}
              </span>
              {dbHealth?.status === 'healthy' ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 dark:text-[#20D6A0]" />
              ) : (
                <AlertCircle className="w-3.5 h-3.5 text-amber-500 dark:text-[#F6BD60]" />
              )}
            </div>

            {/* Simulation Status */}
            {isSimulating && (
              <div className="flex items-center gap-1.5 text-xs text-[#FF784F] bg-orange-50 dark:bg-rose-950/40 px-3 py-1.5 rounded-xl border border-orange-200/90 dark:border-rose-800/60 font-medium">
                <Activity className="w-3.5 h-3.5 animate-spin" />
                <span className="font-mono-code text-[11px]">SOLVER RUNNING</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
