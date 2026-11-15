import React from 'react';

export interface MetricItemProps {
  label: string;
  value: string | number;
  subtext?: string;
  trend?: 'healthy' | 'critical' | 'warning' | 'neutral';
  icon?: React.ReactNode;
  dark?: boolean;
}

export const MetricItem: React.FC<MetricItemProps> = ({
  label,
  value,
  subtext,
  trend = 'neutral',
  icon,
  dark = false
}) => {
  const trendColors = {
    healthy: 'text-emerald-600 dark:text-[#20D6A0]',
    critical: 'text-[#F2653A] dark:text-[#FF5364]',
    warning: 'text-amber-500 dark:text-[#F6BD60]',
    neutral: dark ? 'text-slate-100' : 'text-[#171923] dark:text-[#F5F7FF]'
  };

  const trendBadges = {
    healthy: 'bg-emerald-500/10 text-emerald-600 dark:text-[#20D6A0] border-emerald-500/20',
    critical: 'bg-orange-500/10 dark:bg-rose-500/15 text-[#F2653A] dark:text-[#FF5364] border-orange-500/20 dark:border-rose-500/30',
    warning: 'bg-amber-500/10 text-amber-600 dark:text-[#F6BD60] border-amber-500/20',
    neutral: dark 
      ? 'bg-slate-800 text-slate-300 border-slate-700' 
      : 'bg-slate-100 dark:bg-[#182238] text-slate-600 dark:text-[#929CB3] border-slate-200 dark:border-[#253149]'
  };

  return (
    <div
      className={`p-5 rounded-2xl border transition-all duration-200 relative group overflow-hidden ${
        dark 
          ? 'bg-[#080B14] border-[#253149] text-[#F5F7FF] hover:border-[#4F8CFF]/40' 
          : 'bg-white/95 dark:bg-[#0D1220]/95 border-slate-200/80 dark:border-[#253149] text-[#171923] dark:text-[#F5F7FF] shadow-[0_2px_12px_-2px_rgba(0,0,0,0.02)] dark:shadow-[0_4px_20px_-2px_rgba(0,0,0,0.35)] hover:border-slate-300 dark:hover:border-[#4F8CFF]/40 hover:shadow-md'
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span
          className={`text-[11px] uppercase tracking-wider font-semibold font-mono-code ${
            dark ? 'text-slate-400' : 'text-[#737B8C] dark:text-[#929CB3]'
          }`}
        >
          {label}
        </span>
        {icon && (
          <span className={`p-1.5 rounded-lg border ${trendBadges[trend]}`}>
            {icon}
          </span>
        )}
      </div>

      <div className={`text-3xl font-extrabold tracking-tight font-mono-code ${trendColors[trend]}`}>
        {value}
      </div>

      {subtext && (
        <div
          className={`text-[12px] mt-1.5 flex items-center gap-1.5 ${
            dark ? 'text-slate-400' : 'text-[#737B8C] dark:text-[#929CB3]'
          }`}
        >
          {subtext}
        </div>
      )}
    </div>
  );
};
