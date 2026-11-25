import React, { useState } from 'react';
import {
  GraduationCap,
  LogOut,
  LayoutDashboard,
  Menu,
  X,
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface NavbarProps {
  currentView: string;
  setCurrentView: (view: string) => void;
  setSelectedRollNo?: (rollNo: string | null) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, setCurrentView, setSelectedRollNo }) => {
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigateTo = (view: string, rollNo: string | null = null) => {
    setCurrentView(view);
    if (setSelectedRollNo) setSelectedRollNo(rollNo);
    setMobileMenuOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigateTo('home');
  };

  const navItems = [
    { id: 'home', label: 'Overview' },
    { id: 'student-directory', label: 'Students' },
    { id: 'internship-directory', label: 'Internships' },
    { id: 'about', label: 'About' },
    { id: 'contact', label: 'Contact' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-black/[0.06]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-14 items-center gap-4">
          {/* Brand */}
          <button
            onClick={() => navigateTo('home')}
            className="flex items-center gap-2.5 text-left focus:outline-none group cursor-pointer min-w-0"
          >
            <div className="w-8 h-8 rounded-full bg-[#1D1D1F] flex items-center justify-center text-white shrink-0 group-hover:scale-105 transition-transform">
              <GraduationCap className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-[13px] font-semibold tracking-tight text-[#1D1D1F] truncate">
                Vignan's Institute Of Information Technology
              </div>
            </div>
          </button>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-7">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => navigateTo(item.id)}
                className={`text-xs tracking-tight transition-colors cursor-pointer ${
                  currentView === item.id
                    ? 'text-[#1D1D1F] font-semibold'
                    : 'text-[#6E6E73] hover:text-[#1D1D1F] font-normal'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>

          {/* Actions */}
          <div className="hidden md:flex items-center gap-2.5 shrink-0">
            {user ? (
              <>
                <button
                  onClick={() => navigateTo('admin-dashboard')}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#0071E3] hover:bg-[#0077ED] text-white rounded-full text-xs font-medium transition cursor-pointer"
                >
                  <LayoutDashboard className="w-3.5 h-3.5" />
                  <span>Dashboard</span>
                </button>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-[#F5F5F7] hover:bg-[#E8E8ED] text-[#1D1D1F] rounded-full text-xs font-medium transition cursor-pointer"
                  title="Sign out"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span>Sign out</span>
                </button>
              </>
            ) : (
              <button
                onClick={() => navigateTo('admin-login')}
                className="px-4 py-1.5 bg-[#1D1D1F] hover:bg-black text-white rounded-full text-xs font-medium transition cursor-pointer"
              >
                Admin Portal
              </button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-full text-[#1D1D1F] hover:bg-[#F5F5F7] transition"
              aria-label="Toggle navigation"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-xl border-t border-black/[0.06] px-6 py-5 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => navigateTo(item.id)}
              className={`block w-full text-left py-2.5 text-base font-medium border-b border-black/[0.05] ${
                currentView === item.id ? 'text-[#0071E3]' : 'text-[#1D1D1F]'
              }`}
            >
              {item.label}
            </button>
          ))}

          <div className="pt-4 space-y-2.5">
            {user ? (
              <>
                <button
                  onClick={() => navigateTo('admin-dashboard')}
                  className="w-full py-2.5 bg-[#0071E3] text-white rounded-full text-sm font-medium"
                >
                  Open Admin Dashboard
                </button>
                <button
                  onClick={handleLogout}
                  className="w-full py-2.5 bg-[#F5F5F7] text-[#1D1D1F] rounded-full text-sm font-medium"
                >
                  Sign out
                </button>
              </>
            ) : (
              <button
                onClick={() => navigateTo('admin-login')}
                className="w-full py-2.5 bg-[#1D1D1F] text-white rounded-full text-sm font-medium"
              >
                Admin Portal
              </button>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
