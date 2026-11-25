import React from 'react';
import { Loader2 } from 'lucide-react';

interface TactileButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  icon?: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  className?: string;
}

export const TactileButton: React.FC<TactileButtonProps> = ({
  children,
  icon,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  ...props
}) => {
  const baseClasses = "inline-flex items-center justify-center font-medium rounded-lg transition-all duration-150 active:scale-[0.98] select-none focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const sizeClasses = {
    sm: "px-3 py-1.5 text-xs gap-1.5",
    md: "px-4 py-2 text-sm gap-2",
    lg: "px-6 py-2.5 text-base gap-2.5",
  }[size];

  const variantClasses = {
    primary: "bg-slate-900 text-white hover:bg-slate-800 shadow-sm focus:ring-slate-900 disabled:bg-slate-700",
    secondary: "bg-slate-100 text-slate-900 hover:bg-slate-200 focus:ring-slate-400 disabled:bg-slate-50 disabled:text-slate-400",
    outline: "border border-slate-200 bg-white text-slate-800 hover:bg-slate-50 focus:ring-slate-300 disabled:opacity-50",
    ghost: "bg-transparent text-slate-700 hover:bg-slate-100 focus:ring-slate-300 disabled:opacity-50",
  }[variant];

  return (
    <button
      disabled={disabled || loading}
      className={`${baseClasses} ${sizeClasses} ${variantClasses} ${className}`}
      {...props}
    >
      {loading ? (
        <Loader2 className="w-3.5 h-3.5 animate-spin text-current" />
      ) : (
        icon && <span className="inline-flex shrink-0">{icon}</span>
      )}
      <span>{children}</span>
    </button>
  );
};
