import React from 'react';

interface AssetoCardProps {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
  noPadding?: boolean;
}

export const AssetoCard: React.FC<AssetoCardProps> = ({
  title,
  subtitle,
  action,
  children,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  noPadding = false,
}) => {
  return (
    <div
      className={`bg-white border border-[#E8ECEF] rounded-2xl shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] transition-all duration-200 ${className}`}
    >
      {(title || subtitle || action) && (
        <div
          className={`px-5 py-4 border-b border-[#F1F4F7] flex items-center justify-between gap-3 ${headerClassName}`}
        >
          <div>
            {title && (
              <h3 className="text-base font-semibold text-[#16283B] tracking-tight">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-xs text-[#64748B] mt-0.5 font-normal">
                {subtitle}
              </p>
            )}
          </div>
          {action && <div className="flex items-center gap-2">{action}</div>}
        </div>
      )}
      <div className={noPadding ? bodyClassName : `p-5 ${bodyClassName}`}>
        {children}
      </div>
    </div>
  );
};
