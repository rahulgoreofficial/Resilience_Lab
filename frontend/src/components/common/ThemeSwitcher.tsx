import React from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme, type Theme } from './ThemeProvider';

export interface ThemeSwitcherProps {
  className?: string;
  size?: 'sm' | 'md';
}

export const ThemeSwitcher: React.FC<ThemeSwitcherProps> = ({ className = '', size = 'sm' }) => {
  const { theme, setTheme } = useTheme();

  const options: Array<{ id: Theme; label: string; icon: React.ReactNode }> = [
    { id: 'light', label: 'Light', icon: <Sun className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} /> },
    { id: 'dark', label: 'Dark', icon: <Moon className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} /> },
    { id: 'system', label: 'System', icon: <Monitor className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} /> }
  ];

  return (
    <div
      role="radiogroup"
      aria-label="Theme selection"
      className={`inline-flex items-center p-0.5 rounded-xl bg-slate-100/90 dark:bg-[#121A2B] border border-slate-200/80 dark:border-[#253149] shadow-inner transition-colors ${className}`}
    >
      {options.map((opt) => {
        const isActive = theme === opt.id;
        return (
          <button
            key={opt.id}
            role="radio"
            aria-checked={isActive}
            title={`Set theme to ${opt.label}`}
            onClick={() => setTheme(opt.id)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all duration-200 cursor-pointer ${
              isActive
                ? 'bg-white dark:bg-[#182238] text-indigo-600 dark:text-cyan-400 shadow-sm border border-slate-200/60 dark:border-[#253149]'
                : 'text-slate-500 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF]'
            }`}
          >
            {opt.icon}
            <span className="hidden md:inline text-[11px] font-mono-code">{opt.label}</span>
          </button>
        );
      })}
    </div>
  );
};

