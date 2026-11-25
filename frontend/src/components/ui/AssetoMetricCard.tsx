import React from 'react';
import { LucideIcon } from 'lucide-react';

interface AssetoMetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    variant?: 'blue' | 'emerald' | 'amber' | 'slate';
  };
  onClick?: () => void;
  className?: string;
}

export const AssetoMetricCard: React.FC<AssetoMetricCardProps> = ({
  label,
  value,
  subtext,
  icon: Icon,
  badge,
  onClick,
  className = '',
}) => {
  const badgeClasses = {
    blue: 'bg-[#1758A2]/10 text-[#1758A2] border border-[#1758A2]/20',
    emerald: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    amber: 'bg-amber-50 text-amber-700 border border-amber-200',
    slate: 'bg-slate-100 text-slate-700 border border-slate-200',
  }[badge?.variant || 'blue'];

  return (
    <div
      onClick={onClick}
      className={`bg-white border border-[#E8ECEF] rounded-2xl p-5 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col justify-between transition-all duration-200 ${
        onClick ? 'cursor-pointer hover:border-[#A1BDD4] hover:shadow-[0_4px_16px_0_rgba(23,88,162,0.08)] hover:-translate-y-0.5' : ''
      } ${className}`}
    >
      <div className="flex items-start justify-between gap-3">
        <span className="text-xs font-medium text-[#64748B] uppercase tracking-wider">
          {label}
        </span>
        <div className="w-10 h-10 rounded-xl bg-[#1758A2]/10 text-[#1758A2] flex items-center justify-center shrink-0">
          <Icon className="w-5 h-5 text-[#1758A2]" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-2xl lg:text-3xl font-bold text-[#16283B] tracking-tight">
          {value}
        </div>
        {(subtext || badge) && (
          <div className="mt-2 flex items-center gap-2 flex-wrap text-xs">
            {badge && (
              <span className={`px-2 py-0.5 rounded-full font-semibold text-[11px] ${badgeClasses}`}>
                {badge.text}
              </span>
            )}
            {subtext && (
              <span className="text-[#64748B] text-xs font-normal">
                {subtext}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
