import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'healthy' | 'critical' | 'failed' | 'warning' | 'neutral' | 'cyan' | 'brand' | 'indigo';
  size?: 'sm' | 'md';
  className?: string;
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className = '',
  icon
}) => {
  const variantStyles = {
    healthy: 'bg-emerald-50/90 dark:bg-emerald-500/15 text-emerald-700 dark:text-[#20D6A0] border-emerald-200/90 dark:border-emerald-500/30',
    critical: 'bg-orange-50/90 dark:bg-rose-500/15 text-[#F2653A] dark:text-[#FF5364] border-orange-200/90 dark:border-rose-500/30',
    failed: 'bg-red-50/90 dark:bg-red-500/15 text-red-700 dark:text-[#FF5364] border-red-200/90 dark:border-red-500/30',
    warning: 'bg-amber-50/90 dark:bg-amber-500/15 text-amber-700 dark:text-[#F6BD60] border-amber-200/90 dark:border-amber-500/30',
    cyan: 'bg-cyan-50/90 dark:bg-cyan-500/15 text-cyan-700 dark:text-[#22D3EE] border-cyan-200/90 dark:border-cyan-500/30',
    brand: 'bg-indigo-50/90 dark:bg-indigo-500/15 text-indigo-700 dark:text-[#9B7BFF] border-indigo-200/90 dark:border-indigo-500/30',
    indigo: 'bg-indigo-50/90 dark:bg-indigo-500/15 text-indigo-700 dark:text-[#9B7BFF] border-indigo-200/90 dark:border-indigo-500/30',
    neutral: 'bg-slate-100/90 dark:bg-[#182238] text-slate-700 dark:text-[#929CB3] border-slate-200/90 dark:border-[#253149]'
  };

  const sizeStyles = {
    sm: 'text-[10px] px-2 py-0.5 tracking-wider',
    md: 'text-xs px-2.5 py-1 tracking-wide'
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium rounded-full border uppercase font-mono-code transition-colors ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </span>
  );
};
