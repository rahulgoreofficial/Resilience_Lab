import React from 'react';
import { Loader2 } from 'lucide-react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'brand' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'dark';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  icon?: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 select-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none active:scale-[0.98]';

  const sizeStyles = {
    sm: 'text-xs px-3 py-1.5 gap-1.5 rounded-lg',
    md: 'text-sm px-4 py-2 gap-2 rounded-xl',
    lg: 'text-base px-6 py-2.5 gap-2.5 font-semibold rounded-xl'
  };

  const variantStyles = {
    // Brand Gradient (Indigo -> Blue -> Cyan)
    brand: 'bg-gradient-to-r from-[#6366F1] via-[#4F8CFF] to-[#22D3EE] text-white shadow-md shadow-indigo-500/20 hover:shadow-lg hover:shadow-indigo-500/30 hover:brightness-105 border border-white/20',
    // Primary Brand Orange
    primary: 'bg-gradient-to-r from-[#FF784F] to-[#EA580C] text-white shadow-sm shadow-orange-500/20 hover:shadow-md hover:shadow-orange-500/30 hover:brightness-105 border border-white/10',
    // Secondary Glass White / Dark Elevated
    secondary: 'bg-white/95 dark:bg-[#121A2B] text-[#171923] dark:text-[#F5F7FF] border border-slate-200/90 dark:border-[#253149] shadow-xs hover:bg-slate-50 dark:hover:bg-[#182238] hover:border-slate-300 dark:hover:border-[#4F8CFF]/40',
    // Outline Subtle
    outline: 'border border-slate-300/80 dark:border-[#253149] bg-white/60 dark:bg-[#0D1220]/60 text-[#171923] dark:text-[#F5F7FF] hover:bg-slate-100/80 dark:hover:bg-[#182238] hover:border-slate-400/80 dark:hover:border-[#4F8CFF]/40 backdrop-blur-xs',
    // Ghost
    ghost: 'text-slate-600 dark:text-[#929CB3] hover:text-slate-900 dark:hover:text-[#F5F7FF] hover:bg-slate-100/70 dark:hover:bg-[#182238]/70',
    // Danger Red
    danger: 'bg-gradient-to-r from-[#FF5364] to-[#DC2626] text-white shadow-sm shadow-red-500/20 hover:brightness-105 border border-white/10',
    // Dark Canvas
    dark: 'bg-[#080B14] text-[#F5F7FF] border border-[#253149] hover:bg-[#121A2B] shadow-xs'
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <Loader2 className="w-4 h-4 animate-spin text-current shrink-0" />
      ) : icon ? (
        <span className="shrink-0">{icon}</span>
      ) : null}
      {children}
    </button>
  );
};
