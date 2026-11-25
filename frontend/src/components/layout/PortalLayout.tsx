import React, { useState } from 'react';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  FileSpreadsheet,
  FileText,
  BarChart3,
  ShieldCheck,
  Settings,
  Activity,
  LogOut,
  ArrowLeft,
  Menu,
  CheckSquare,
  X,
  UserPlus,
  Search,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  TrendingUp,
  SlidersHorizontal,
  Bell
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { StudentAvatar } from '../ui/StudentAvatar';

interface PortalLayoutProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  setCurrentView: (view: string) => void;
  children: React.ReactNode;
}

export const PortalLayout: React.FC<PortalLayoutProps> = ({
  currentTab,
  setCurrentTab,
  setCurrentView,
  children,
}) => {
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [globalSearch, setGlobalSearch] = useState('');

  const roleUpper = user?.role?.toUpperCase() || '';
  const isAdmin = roleUpper.includes('ADMIN') || roleUpper === 'REVIEWER';

  // Navigation organized into Asseto logical groups
  const navigationGroups = [
    {
      group: 'OVERVIEW',
      items: [
        { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
      ],
    },
    {
      group: 'MANAGEMENT',
      items: [
        { id: 'students', label: 'Students Directory', icon: Users },
        { id: 'internships', label: 'Internships & Placements', icon: Briefcase },
        { id: 'excel-import', label: 'Document Staging', icon: FileSpreadsheet },
        { id: 'pdf-upload', label: 'PDF Data Extraction', icon: FileText },
        ...(isAdmin ? [
          { id: 'import-approvals', label: 'Approvals Queue', icon: CheckSquare },
        ] : []),
      ],
    },
    {
      group: 'ANALYTICS',
      items: [
        { id: 'reports', label: 'Reports & Exports', icon: BarChart3 },
        { id: 'statistics', label: 'Institutional Metrics', icon: TrendingUp },
      ],
    },
    ...(isAdmin ? [
      {
        group: 'SYSTEM',
        items: [
          { id: 'clients', label: 'User Accounts', icon: UserPlus },
          { id: 'permissions', label: 'Public Permissions', icon: ShieldCheck },
          { id: 'audit-logs', label: 'Activity Logs', icon: Activity },
          { id: 'settings', label: 'Portal Settings', icon: Settings },
        ],
      },
    ] : []),
  ];

  const handleLogout = () => {
    logout();
    setCurrentView('home');
  };

  // Active page title helper
  const getActiveTitle = () => {
    for (const grp of navigationGroups) {
      for (const item of grp.items) {
        if (item.id === currentTab) return item.label;
      }
    }
    if (currentTab === 'statistics') return 'Institutional Metrics';
    return 'Dashboard Overview';
  };

  const handleTabClick = (tabId: string) => {
    if (tabId === 'statistics') {
      setCurrentTab('dashboard');
    } else {
      setCurrentTab(tabId);
    }
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#F6F6F6] text-[#16283B] flex overflow-x-hidden font-sans">
      {/* Desktop Sidebar */}
      <aside
        className={`hidden lg:flex flex-col bg-white border-r border-[#E8ECEF] shrink-0 transition-all duration-200 z-30 select-none ${
          isCollapsed ? 'w-20' : 'w-64'
        }`}
      >
        {/* Brand Header */}
        <div className="h-16 px-4 border-b border-[#F1F4F7] flex items-center justify-between">
          {!isCollapsed ? (
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-[#1758A2] text-white flex items-center justify-center font-bold text-lg shadow-sm">
                S
              </div>
              <div className="overflow-hidden">
                <div className="font-bold text-sm tracking-tight text-[#16283B] flex items-center gap-1.5 truncate">
                  <span>StudentPortal</span>
                  <span className="text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded-full bg-[#1758A2]/10 text-[#1758A2]">
                    {isAdmin ? 'ADMIN' : 'CLIENT'}
                  </span>
                </div>
                <div className="text-[11px] text-[#64748B] truncate">
                  Institutional SaaS
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto w-9 h-9 rounded-xl bg-[#1758A2] text-white flex items-center justify-center font-bold text-lg shadow-sm">
              S
            </div>
          )}

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1.5 text-[#64748B] hover:text-[#16283B] hover:bg-[#F1F4F7] rounded-lg transition"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Back to Public Web Link */}
        <div className="p-3">
          <button
            onClick={() => setCurrentView('home')}
            className={`w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-[#64748B] hover:text-[#1758A2] hover:bg-[#F1F4F7] rounded-xl transition ${
              isCollapsed ? 'justify-center px-0' : ''
            }`}
            title="Return to Public Website"
          >
            <ArrowLeft className="w-4 h-4 shrink-0" />
            {!isCollapsed && <span>Public Website</span>}
          </button>
        </div>

        {/* Navigation Groups */}
        <nav className="flex-1 px-3 py-2 space-y-6 overflow-y-auto">
          {navigationGroups.map((group) => (
            <div key={group.group} className="space-y-1">
              {!isCollapsed && (
                <div className="px-3 pb-1 text-[11px] font-semibold text-[#94A3B8] tracking-wider uppercase">
                  {group.group}
                </div>
              )}
              {group.items.map((item) => {
                const Icon = item.icon;
                const active = currentTab === item.id || (item.id === 'statistics' && currentTab === 'dashboard');
                return (
                  <button
                    key={item.id}
                    onClick={() => handleTabClick(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                      isCollapsed ? 'justify-center px-0' : ''
                    } ${
                      active
                        ? 'bg-[#1758A2] text-white shadow-sm font-semibold'
                        : 'text-[#64748B] hover:text-[#16283B] hover:bg-[#F8FAFC]'
                    }`}
                    title={isCollapsed ? item.label : undefined}
                  >
                    <Icon className={`w-4 h-4 shrink-0 ${active ? 'text-white' : 'text-[#64748B]'}`} />
                    {!isCollapsed && <span className="truncate">{item.label}</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Administrator Profile Card */}
        <div className="p-3 border-t border-[#F1F4F7] bg-[#FAFAFA]">
          <div
            className={`flex items-center gap-3 p-2 rounded-xl bg-white border border-[#E8ECEF] ${
              isCollapsed ? 'justify-center p-1.5' : ''
            }`}
          >
            <StudentAvatar
              name={user?.full_name || 'Admin'}
              size="sm"
            />
            {!isCollapsed && (
              <div className="min-w-0 flex-1">
                <div className="text-xs font-semibold text-[#16283B] truncate">
                  {user?.full_name || 'System User'}
                </div>
                <div className="text-[10px] text-[#64748B] truncate">
                  {user?.email || 'admin@institution.edu'}
                </div>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="p-1.5 text-[#64748B] hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Navigation Bar */}
        <header className="h-16 bg-white border-b border-[#E8ECEF] px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4 shrink-0 z-20">
          {/* Left: Mobile hamburger + Active Page Breadcrumb */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 text-[#64748B] hover:text-[#16283B] hover:bg-[#F1F4F7] rounded-xl transition"
              title="Open Navigation Menu"
            >
              <Menu className="w-5 h-5" />
            </button>

            <div>
              <div className="flex items-center gap-2 text-xs text-[#64748B]">
                <span>Portal</span>
                <span>/</span>
                <span className="font-semibold text-[#1758A2]">{getActiveTitle()}</span>
              </div>
              <h1 className="text-sm lg:text-base font-bold text-[#16283B] tracking-tight">
                {getActiveTitle()}
              </h1>
            </div>
          </div>

          {/* Center: Search input */}
          <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
            <div className="relative w-full">
              <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={globalSearch}
                onChange={(e) => setGlobalSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && globalSearch.trim()) {
                    setCurrentTab('students');
                  }
                }}
                placeholder="Search students, roll no, organizations..."
                className="w-full pl-9 pr-12 py-2 text-xs bg-[#F6F6F6] hover:bg-[#F1F4F7] focus:bg-white border border-[#E8ECEF] focus:border-[#1758A2] rounded-xl outline-none transition text-[#16283B] placeholder:text-[#94A3B8]"
              />
              <kbd className="absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-mono font-medium text-[#94A3B8] bg-white px-1.5 py-0.5 rounded border border-[#E8ECEF]">
                ⌘K
              </kbd>
            </div>
          </div>

          {/* Right: Actions, Status badge & User avatar */}
          <div className="flex items-center gap-3">
            {/* Real DB Status indicator */}
            <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/80 text-[11px] font-medium text-emerald-700">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>DB Connected</span>
            </div>

            {/* Quick Action Button */}
            <button
              onClick={() => setCurrentTab('students')}
              className="asseto-btn-primary text-xs py-1.5 px-3 rounded-xl hidden sm:inline-flex"
            >
              <span>Students</span>
            </button>

            {/* Profile pill on header */}
            <div className="flex items-center gap-2 pl-2 border-l border-[#E8ECEF]">
              <StudentAvatar
                name={user?.full_name || 'Admin'}
                size="sm"
              />
              <div className="hidden xl:block text-left">
                <div className="text-xs font-semibold text-[#16283B] leading-tight">
                  {user?.full_name || 'Admin'}
                </div>
                <div className="text-[10px] font-mono text-[#64748B]">
                  {user?.role}
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Mobile Navigation Drawer Backdrop */}
        {sidebarOpen && (
          <div
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
          />
        )}

        {/* Mobile Sidebar Drawer */}
        <aside
          className={`fixed top-0 bottom-0 left-0 w-72 bg-white border-r border-[#E8ECEF] z-50 flex flex-col transform transition-transform duration-200 ease-in-out lg:hidden ${
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          {/* Drawer Header */}
          <div className="h-16 px-4 border-b border-[#F1F4F7] flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-[#1758A2] text-white flex items-center justify-center font-bold text-base shadow-sm">
                S
              </div>
              <span className="font-bold text-sm text-[#16283B]">StudentPortal</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1.5 text-[#64748B] hover:text-[#16283B] rounded-lg"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-3">
            <button
              onClick={() => {
                setCurrentView('home');
                setSidebarOpen(false);
              }}
              className="w-full flex items-center gap-2 px-3 py-2 text-xs font-medium text-[#1758A2] bg-[#1758A2]/10 rounded-xl"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Return to Public Website</span>
            </button>
          </div>

          <nav className="flex-1 px-3 py-2 space-y-5 overflow-y-auto">
            {navigationGroups.map((group) => (
              <div key={group.group} className="space-y-1">
                <div className="px-3 pb-1 text-[11px] font-semibold text-[#94A3B8] tracking-wider uppercase">
                  {group.group}
                </div>
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = currentTab === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => handleTabClick(item.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium ${
                        active
                          ? 'bg-[#1758A2] text-white font-semibold shadow-sm'
                          : 'text-[#64748B] hover:bg-[#F8FAFC]'
                      }`}
                    >
                      <Icon className={`w-4 h-4 ${active ? 'text-white' : 'text-[#64748B]'}`} />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            ))}
          </nav>

          <div className="p-4 border-t border-[#F1F4F7] flex items-center justify-between text-xs">
            <div>
              <div className="font-semibold text-[#16283B]">{user?.full_name}</div>
              <div className="text-[11px] text-[#64748B]">{user?.role}</div>
            </div>
            <button onClick={handleLogout} className="text-rose-600 font-medium hover:underline">
              Sign out
            </button>
          </div>
        </aside>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};
