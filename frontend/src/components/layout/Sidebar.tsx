import React from 'react';
import { 
  LayoutDashboard, 
  Network, 
  PlayCircle, 
  Activity, 
  History, 
  GitCompare, 
  FileText, 
  GraduationCap, 
  Sliders, 
  ChevronRight 
} from 'lucide-react';

export type ActivePage = 
  | 'dashboard' 
  | 'topology' 
  | 'simulation' 
  | 'analytics' 
  | 'history' 
  | 'comparison'
  | 'design-studio'
  | 'guide';

export interface SidebarProps {
  activePage: ActivePage;
  onNavigate: (page: ActivePage) => void;
  onOpenReport?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activePage,
  onNavigate,
  onOpenReport
}) => {
  const navItems: Array<{ id: ActivePage; label: string; icon: React.ReactNode; badge?: string; badgeColor?: string }> = [
    { id: 'dashboard', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'topology', label: 'Network Topology', icon: <Network className="w-4 h-4" /> },
    { id: 'simulation', label: 'Simulation Lab', icon: <PlayCircle className="w-4 h-4" /> },
    { id: 'analytics', label: 'Resilience Analytics', icon: <Activity className="w-4 h-4" /> },
    { id: 'design-studio', label: 'Resilience Design Studio', icon: <Sliders className="w-4 h-4" />, badge: 'STUDIO', badgeColor: 'bg-indigo-50 dark:bg-indigo-950/50 text-indigo-600 dark:text-[#9B7BFF] border-indigo-200/80 dark:border-indigo-800/60' },
    { id: 'comparison', label: 'Scenario Comparison', icon: <GitCompare className="w-4 h-4" /> },
    { id: 'history', label: 'Run History', icon: <History className="w-4 h-4" /> },
    { id: 'guide', label: 'Interactive 3D Guide', icon: <GraduationCap className="w-4 h-4" />, badge: '3D LAB', badgeColor: 'bg-cyan-50 dark:bg-cyan-950/50 text-cyan-600 dark:text-[#22D3EE] border-cyan-200/80 dark:border-cyan-800/60' },
  ];

  return (
    <aside className="w-full md:w-64 lg:w-68 bg-white/80 dark:bg-[#080B14]/85 backdrop-blur-md border-r border-slate-200/80 dark:border-[#253149] shrink-0 flex flex-col justify-between rounded-3xl p-4 shadow-[0_2px_12px_rgba(0,0,0,0.02)] dark:shadow-[0_4px_24px_rgba(0,0,0,0.4)] transition-colors">
      <div className="space-y-2">
        <div className="px-3.5 pt-2 pb-1 text-[11px] font-bold uppercase tracking-wider text-[#737B8C] dark:text-[#929CB3] font-mono-code">
          Platform Suite
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => {
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-2xl text-sm font-medium transition-all duration-200 cursor-pointer group ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-50/90 via-blue-50/70 to-cyan-50/40 dark:from-[#121A2B] dark:via-[#182238] dark:to-[#121A2B] text-slate-900 dark:text-[#F5F7FF] font-semibold border border-indigo-200/70 dark:border-[#4F8CFF]/50 shadow-xs dark:shadow-[0_0_16px_rgba(79,140,255,0.2)]'
                    : 'text-slate-600 dark:text-[#929CB3] hover:bg-slate-100/70 dark:hover:bg-[#121A2B] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`p-1.5 rounded-xl transition-colors ${
                    isActive 
                      ? 'bg-gradient-to-r from-[#6366F1] to-[#4F8CFF] text-white shadow-xs' 
                      : 'text-slate-500 dark:text-slate-400 group-hover:text-slate-800 dark:group-hover:text-[#F5F7FF] group-hover:bg-slate-200/60 dark:group-hover:bg-[#182238]'
                  }`}>
                    {item.icon}
                  </span>
                  <span className="tracking-tight">{item.label}</span>
                </div>
                {item.badge ? (
                  <span className={`text-[10px] font-mono-code px-2 py-0.5 rounded-full border font-semibold ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                ) : isActive ? (
                  <ChevronRight className="w-4 h-4 text-indigo-500 dark:text-cyan-400" />
                ) : null}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Audit Trigger */}
      <div className="pt-4 border-t border-slate-100 dark:border-[#253149] space-y-3">
        {onOpenReport && (
          <button
            onClick={onOpenReport}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-xs font-semibold text-slate-800 dark:text-[#F5F7FF] bg-white dark:bg-[#0D1220] border border-slate-200/90 dark:border-[#253149] rounded-2xl hover:bg-slate-50 dark:hover:bg-[#182238] hover:border-slate-300 dark:hover:border-[#4F8CFF]/40 transition-all shadow-xs cursor-pointer group"
          >
            <FileText className="w-4 h-4 text-[#FF784F] group-hover:scale-110 transition-transform" />
            <span>Resilience Audit Report</span>
          </button>
        )}
        <div className="px-2 text-[11px] text-[#737B8C] dark:text-[#929CB3] space-y-0.5">
          <p className="font-semibold text-slate-700 dark:text-slate-300">Discrete Mathematics Engine</p>
          <p className="text-[10px] text-slate-400 dark:text-[#69758E] font-mono-code">Spectral Graph Resilience v2.4</p>
        </div>
      </div>
    </aside>
  );
};
