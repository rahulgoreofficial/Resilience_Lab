import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
  dark?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  header,
  footer,
  dark = false
}) => {
  return (
    <div
      className={`rounded-2xl transition-all duration-200 overflow-hidden ${
        dark 
          ? 'bg-gradient-to-br from-[#080B14] via-[#0D1220] to-[#121A2B] text-[#F5F7FF] border border-[#253149] shadow-xl' 
          : 'bg-white/95 dark:bg-[#0D1220]/92 text-[#171923] dark:text-[#F5F7FF] border border-slate-200/80 dark:border-[#253149] shadow-[0_4px_20px_-2px_rgba(0,0,0,0.03)] dark:shadow-[0_8px_32px_-4px_rgba(0,0,0,0.4)] backdrop-blur-md'
      } ${className}`}
    >
      {header && (
        <div
          className={`px-6 py-4.5 border-b ${
            dark 
              ? 'border-[#253149] bg-[#0D1220]/60' 
              : 'border-slate-100 dark:border-[#253149] bg-slate-50/50 dark:bg-[#121A2B]/60'
          }`}
        >
          {header}
        </div>
      )}
      <div className="p-6">{children}</div>
      {footer && (
        <div
          className={`px-6 py-3.5 border-t ${
            dark 
              ? 'border-[#253149] bg-[#0D1220]/80' 
              : 'border-slate-100 dark:border-[#253149] bg-slate-50/70 dark:bg-[#121A2B]/80'
          }`}
        >
          {footer}
        </div>
      )}
    </div>
  );
};
