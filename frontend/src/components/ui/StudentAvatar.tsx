import React, { useState } from 'react';
import { User } from 'lucide-react';

interface StudentAvatarProps {
  rollNo?: string;
  name?: string;
  photoPath?: string | null;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  className?: string;
  timestamp?: number;
}

export const StudentAvatar: React.FC<StudentAvatarProps> = ({
  rollNo,
  name,
  photoPath,
  size = 'md',
  className = '',
  timestamp,
}) => {
  const [imageError, setImageError] = useState(false);

  // Compute initials from full name or roll no
  const getInitials = (n?: string, r?: string) => {
    if (n && n.trim()) {
      const parts = n.trim().split(/\s+/);
      if (parts.length >= 2) {
        return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
      }
      return n.substring(0, 2).toUpperCase();
    }
    if (r && r.trim()) {
      return r.substring(0, 2).toUpperCase();
    }
    return 'ST';
  };

  const sizeClasses = {
    xs: 'w-7 h-7 text-[10px]',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-14 h-14 text-base font-semibold',
    xl: 'w-20 h-20 text-xl font-bold',
    '2xl': 'w-28 h-28 text-2xl font-bold',
  }[size];

  // Resolve image URL
  const getImageUrl = () => {
    const t = timestamp ? `&t=${timestamp}` : '';
    if (photoPath && photoPath.trim()) {
      const clean = photoPath.replace(/\\/g, '/');
      return `/api/v1/documents/view?path=${encodeURIComponent(clean)}${t}`;
    }
    if (rollNo && rollNo.trim()) {
      return `/api/v1/public/photo/${encodeURIComponent(rollNo.trim())}${timestamp ? `?t=${timestamp}` : ''}`;
    }
    return null;
  };

  const imgUrl = getImageUrl();
  const initials = getInitials(name, rollNo);

  if (!imgUrl || imageError) {
    return (
      <div
        className={`${sizeClasses} rounded-full bg-[#1758A2]/10 text-[#1758A2] border border-[#1758A2]/20 flex items-center justify-center font-semibold select-none shrink-0 ${className}`}
        title={name || rollNo || 'Student'}
      >
        {initials || <User className="w-1/2 h-1/2 opacity-70" />}
      </div>
    );
  }

  return (
    <div
      className={`${sizeClasses} rounded-full overflow-hidden bg-slate-100 border border-[#E8ECEF] shrink-0 relative flex items-center justify-center ${className}`}
    >
      <img
        src={imgUrl}
        alt={name || rollNo || 'Student Photo'}
        className="w-full h-full object-cover rounded-full"
        loading="lazy"
        onError={() => setImageError(true)}
      />
    </div>
  );
};
