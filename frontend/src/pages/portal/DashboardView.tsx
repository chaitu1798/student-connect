import React, { useState, useEffect } from 'react';
import {
  Users,
  Briefcase,
  Building2,
  FileSpreadsheet,
  FileText,
  UserPlus,
  RefreshCw,
  GraduationCap,
  ShieldCheck,
  Award,
  ArrowUpRight,
  TrendingUp,
  CheckCircle2,
  Clock,
  Sparkles,
  Layers,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { DashboardStats } from '../../types';
import { AssetoCard } from '../../components/ui/AssetoCard';
import { AssetoMetricCard } from '../../components/ui/AssetoMetricCard';
import { StudentAvatar } from '../../components/ui/StudentAvatar';

interface DashboardViewProps {
  setCurrentTab: (tab: string) => void;
  isAdmin?: boolean;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ setCurrentTab, isAdmin }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());
  const [activeCategory, setActiveCategory] = useState<'all' | 'students' | 'internships' | 'academics'>('all');
  const [fetchError, setFetchError] = useState('');

  const fetchDashboardStats = async (isManualRefresh = false) => {
    if (isManualRefresh) setRefreshing(true);
    setFetchError('');
    try {
      const res = await apiClient.get('/admin/dashboard-stats');
      setStats(res.data);
      setLastRefreshed(new Date());
    } catch (err: any) {
      console.error('Error fetching dashboard statistics:', err);
      setFetchError(err.response?.data?.detail || 'Unable to connect to live database analytics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
  }, []);

  if (loading) {
    return (
      <div className="py-24 text-center space-y-4">
        <div className="w-10 h-10 border-3 border-[#1758A2] border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm font-semibold text-[#16283B]">Loading institutional database records</p>
        <p className="text-xs text-[#64748B]">Querying verified student, academic, and internship metrics...</p>
      </div>
    );
  }

  // Exact calculations from database records
  const totalStudents = stats?.total_students || 0;
  const completedProfiles = stats?.completed_profiles ?? 0;
  const incompleteProfiles = stats?.incomplete_profiles ?? Math.max(0, totalStudents - completedProfiles);
  const completionRate = totalStudents > 0 ? Math.round((completedProfiles / totalStudents) * 100) : 0;

  const totalInternships = stats?.total_internships || 0;
  const studentsWithInternships = stats?.students_with_internships ?? 0;
  const studentsWithoutInternships = stats?.students_without_internships ?? Math.max(0, totalStudents - studentsWithInternships);

  const avgCgpa = stats?.average_ug_cgpa ?? stats?.avg_cgpa ?? 0;
  const withBacklogs = stats?.students_with_backlogs || 0;
  const withoutBacklogs = stats?.students_without_backlogs ?? Math.max(0, totalStudents - withBacklogs);
  const crtRegistered = stats?.crt_registered_count || 0;

  const certReceived = stats?.certificates_received ?? 0;
  const certPending = stats?.certificates_pending ?? Math.max(0, totalInternships - certReceived);

  // Gender counts
  const maleCount = stats?.gender_distribution?.Male ?? stats?.gender_distribution?.male ?? 0;
  const femaleCount = stats?.gender_distribution?.Female ?? stats?.gender_distribution?.female ?? 0;

  // Branch entries
  const branchEntries = stats?.branch_distribution ? Object.entries(stats.branch_distribution) : [];
  const maxBranchCount = branchEntries.length > 0 ? Math.max(...branchEntries.map(([_, c]) => c)) : 1;

  // Year entries (Batch distribution)
  const yearEntries = stats?.year_distribution ? Object.entries(stats.year_distribution) : [];

  // Organization entries
  const orgEntries = stats?.organization_distribution ? Object.entries(stats.organization_distribution).slice(0, 8) : [];
  const maxOrgCount = orgEntries.length > 0 ? Math.max(...orgEntries.map(([_, c]) => c)) : 1;

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Asseto Welcome & Action Header */}
      <div className="bg-white border border-[#E8ECEF] rounded-2xl p-6 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
            <span className="w-2 h-2 rounded-full bg-[#1758A2]"></span>
            <span>Institutional Management Portal</span>
            <span>•</span>
            <span className="text-[#64748B] font-normal">Real-Time Database Records</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
            System Overview & Governance
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Verified student credentials, corporate internships, academic records, and live system analytics.
          </p>
        </div>

        {/* Quick Action Toolbar */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={() => fetchDashboardStats(true)}
            disabled={refreshing}
            className="asseto-btn-secondary text-xs py-2 px-3.5 rounded-xl"
            title="Refresh database records"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#64748B] ${refreshing ? 'animate-spin text-[#1758A2]' : ''}`} />
            <span>{refreshing ? 'Syncing...' : 'Sync DB'}</span>
          </button>

          <button
            onClick={() => setCurrentTab('excel-import')}
            className="asseto-btn-secondary text-xs py-2 px-3.5 rounded-xl"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-[#64748B]" />
            <span>Import Excel</span>
          </button>

          <button
            onClick={() => setCurrentTab('reports')}
            className="asseto-btn-secondary text-xs py-2 px-3.5 rounded-xl"
          >
            <FileText className="w-3.5 h-3.5 text-[#64748B]" />
            <span>Export Reports</span>
          </button>

          <button
            onClick={() => setCurrentTab('students')}
            className="asseto-btn-primary text-xs py-2 px-4 rounded-xl"
          >
            <UserPlus className="w-3.5 h-3.5 text-white" />
            <span>Manage Students</span>
          </button>
        </div>
      </div>

      {fetchError && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-2xl text-xs flex items-center justify-between">
          <span>{fetchError}</span>
          <button onClick={() => fetchDashboardStats(true)} className="underline font-semibold ml-2">
            Retry
          </button>
        </div>
      )}

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          { id: 'all', label: 'All Analytics' },
          { id: 'students', label: 'Student Demographics' },
          { id: 'internships', label: 'Internships & Placements' },
          { id: 'academics', label: 'Academic Standing' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveCategory(tab.id as any)}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all shrink-0 ${
              activeCategory === tab.id
                ? 'bg-[#1758A2] text-white shadow-xs'
                : 'bg-white border border-[#E8ECEF] text-[#64748B] hover:text-[#16283B] hover:bg-[#F8FAFC]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Primary KPI Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <AssetoMetricCard
          label="Total Enrolled Students"
          value={totalStudents}
          subtext={`${completionRate}% verified profiles`}
          icon={Users}
          badge={{ text: `${totalStudents} Active`, variant: 'blue' }}
          onClick={() => setCurrentTab('students')}
        />

        <AssetoMetricCard
          label="Gender Demographics"
          value={`${maleCount}M : ${femaleCount}F`}
          subtext={`${maleCount} Male • ${femaleCount} Female`}
          icon={ShieldCheck}
          badge={{ text: 'Verified', variant: 'emerald' }}
          onClick={() => setCurrentTab('students')}
        />

        <AssetoMetricCard
          label="Total Internships"
          value={totalInternships}
          subtext={`${studentsWithInternships} students placed`}
          icon={Briefcase}
          badge={{ text: `${certReceived} Certified`, variant: 'emerald' }}
          onClick={() => setCurrentTab('internships')}
        />

        <AssetoMetricCard
          label="Academic Performance"
          value={avgCgpa > 0 ? avgCgpa.toFixed(2) : 'N/A'}
          subtext={`${withBacklogs} with backlogs • ${withoutBacklogs} clean`}
          icon={GraduationCap}
          badge={{ text: `Avg CGPA`, variant: 'amber' }}
          onClick={() => setCurrentTab('reports')}
        />
      </div>

      {/* Secondary Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-[#E8ECEF] rounded-2xl p-4 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-[#64748B] uppercase tracking-wider">
              Departments / Branches
            </div>
            <div className="text-xl font-bold text-[#16283B] mt-0.5">
              {branchEntries.length || stats?.total_branches || 7} Branches
            </div>
            <div className="text-[11px] text-[#1758A2] mt-1 font-medium">
              CSE, ECE, IT, EEE & others
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-[#1758A2]/10 text-[#1758A2] flex items-center justify-center">
            <Layers className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white border border-[#E8ECEF] rounded-2xl p-4 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-[#64748B] uppercase tracking-wider">
              Partner Organizations
            </div>
            <div className="text-xl font-bold text-[#16283B] mt-0.5">
              {stats?.total_organizations || orgEntries.length || 8} Recruiters
            </div>
            <div className="text-[11px] text-emerald-600 mt-1 font-medium">
              Active corporate partners
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Building2 className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white border border-[#E8ECEF] rounded-2xl p-4 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-[#64748B] uppercase tracking-wider">
              CRT Training
            </div>
            <div className="text-xl font-bold text-[#16283B] mt-0.5">
              {crtRegistered} Registered
            </div>
            <div className="text-[11px] text-[#64748B] mt-1">
              Campus placement enrolled
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
            <Award className="w-4 h-4" />
          </div>
        </div>

        <div className="bg-white border border-[#E8ECEF] rounded-2xl p-4 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex items-center justify-between">
          <div>
            <div className="text-[11px] font-medium text-[#64748B] uppercase tracking-wider">
              Certificates Pending
            </div>
            <div className="text-xl font-bold text-[#16283B] mt-0.5">
              {certPending} Pending
            </div>
            <div className="text-[11px] text-amber-600 mt-1 font-medium">
              {certReceived} already verified
            </div>
          </div>
          <div className="w-9 h-9 rounded-xl bg-slate-100 text-[#64748B] flex items-center justify-center">
            <Clock className="w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Main Visual Content Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Charts and Department Distribution (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Department-Wise Distribution */}
          <AssetoCard
            title="Department-Wise Student Distribution"
            subtitle="Real database enrolment distribution across institutional academic engineering streams"
            action={
              <button
                onClick={() => setCurrentTab('students')}
                className="text-xs font-semibold text-[#1758A2] hover:underline inline-flex items-center gap-1"
              >
                <span>View all</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            }
          >
            <div className="space-y-4">
              {branchEntries.length === 0 ? (
                <div className="py-8 text-center text-xs text-[#64748B]">
                  No branch records found in database.
                </div>
              ) : (
                branchEntries.map(([branchName, count]) => {
                  const pct = totalStudents > 0 ? Math.round((count / totalStudents) * 100) : 0;
                  return (
                    <div key={branchName} className="space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-[#16283B]">{branchName}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-[#64748B]">{count} students</span>
                          <span className="font-semibold text-[#1758A2] bg-[#1758A2]/10 px-2 py-0.5 rounded-full text-[11px]">
                            {pct}%
                          </span>
                        </div>
                      </div>
                      <div className="w-full h-2 rounded-full bg-[#F1F4F7] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[#1758A2] transition-all duration-500"
                          style={{ width: `${Math.max(5, (count / maxBranchCount) * 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </AssetoCard>

          {/* Student Growth / Batch Analytics */}
          <AssetoCard
            title="Batch Enrolment & Graduation Year Distribution"
            subtitle="Graduation cohort metrics derived from student academic profiles"
          >
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {yearEntries.length === 0 ? (
                <div className="col-span-full py-4 text-center text-xs text-[#64748B]">
                  Enrolment cohorts will populate once graduation years are recorded.
                </div>
              ) : (
                yearEntries.map(([yr, count]) => (
                  <div
                    key={yr}
                    className="p-3.5 rounded-xl bg-[#F6F6F6] border border-[#E8ECEF] text-center"
                  >
                    <div className="text-[11px] font-medium text-[#64748B]">Class of {yr}</div>
                    <div className="text-xl font-bold text-[#16283B] mt-1">{count}</div>
                    <div className="text-[10px] text-[#1758A2] font-semibold mt-0.5">
                      {totalStudents > 0 ? Math.round((count / totalStudents) * 100) : 0}% of total
                    </div>
                  </div>
                ))
              )}
            </div>
          </AssetoCard>

          {/* Corporate Partner Placements Distribution */}
          <AssetoCard
            title="Top Corporate Placement Organizations"
            subtitle="Verified recruiters hosting student internships"
            action={
              <button
                onClick={() => setCurrentTab('internships')}
                className="text-xs font-semibold text-[#1758A2] hover:underline inline-flex items-center gap-1"
              >
                <span>Internships</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            }
          >
            <div className="space-y-3">
              {orgEntries.length === 0 ? (
                <div className="py-6 text-center text-xs text-[#64748B]">
                  No organizational placements registered yet.
                </div>
              ) : (
                orgEntries.map(([orgName, count]) => {
                  return (
                    <div
                      key={orgName}
                      className="flex items-center justify-between p-2.5 rounded-xl hover:bg-[#F8FAFC] transition border border-transparent hover:border-[#E8ECEF]"
                    >
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-[#1758A2]/10 text-[#1758A2] flex items-center justify-center font-bold text-xs">
                          {orgName.substring(0, 2).toUpperCase()}
                        </div>
                        <div>
                          <div className="text-xs font-semibold text-[#16283B]">{orgName}</div>
                          <div className="text-[11px] text-[#64748B]">Verified Corporate Partner</div>
                        </div>
                      </div>
                      <span className="asseto-badge-blue text-[11px]">
                        {count} {count === 1 ? 'Intern' : 'Interns'}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </AssetoCard>
        </div>

        {/* Right Column: Recently Registered Students & Activity Stream (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Recently Registered / Updated Students */}
          <AssetoCard
            title="Recently Registered Students"
            subtitle="Latest active student directory profiles"
            action={
              <button
                onClick={() => setCurrentTab('students')}
                className="text-xs font-semibold text-[#1758A2] hover:underline"
              >
                View all
              </button>
            }
            noPadding
          >
            <div className="divide-y divide-[#F1F4F7]">
              {(!stats?.recently_updated_students || stats.recently_updated_students.length === 0) ? (
                <div className="p-6 text-center text-xs text-[#64748B]">
                  No student records registered yet.
                </div>
              ) : (
                stats.recently_updated_students.map((st) => (
                  <div
                    key={st.roll_no}
                    onClick={() => setCurrentTab('students')}
                    className="p-3.5 hover:bg-[#F8FAFC] flex items-center justify-between gap-3 cursor-pointer transition"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <StudentAvatar
                        rollNo={st.roll_no}
                        name={st.full_name}
                        size="sm"
                      />
                      <div className="min-w-0">
                        <div className="text-xs font-semibold text-[#16283B] truncate">
                          {st.full_name}
                        </div>
                        <div className="text-[11px] text-[#64748B] flex items-center gap-2">
                          <span className="font-mono text-[#1758A2]">{st.roll_no}</span>
                          <span>•</span>
                          <span className="truncate">{st.branch}</span>
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-[#94A3B8] shrink-0" />
                  </div>
                ))
              )}
            </div>
          </AssetoCard>

          {/* Recent Corporate Engagements & Activities */}
          <AssetoCard
            title="Recent Internship Engagements"
            subtitle="Verified placement records"
            noPadding
          >
            <div className="divide-y divide-[#F1F4F7]">
              {(!stats?.recent_internships || stats.recent_internships.length === 0) ? (
                <div className="p-6 text-center text-xs text-[#64748B]">
                  No internship activities recorded yet.
                </div>
              ) : (
                stats.recent_internships.map((int, idx) => (
                  <div key={idx} className="p-3.5 hover:bg-[#F8FAFC] transition">
                    <div className="flex items-start justify-between gap-2">
                      <div className="text-xs font-semibold text-[#16283B]">
                        {int.full_name}
                      </div>
                      <span className="text-[10px] font-mono text-[#64748B] shrink-0">
                        {int.roll_no}
                      </span>
                    </div>
                    <div className="text-[11px] text-[#1758A2] font-medium mt-0.5">
                      {int.role} @ {int.organization}
                    </div>
                  </div>
                ))
              )}
            </div>
          </AssetoCard>

          {/* Quick Institutional Action Cards */}
          <div className="bg-[#1758A2] rounded-2xl p-5 text-white shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-[#A1BDD4]" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#A1BDD4]">
                Administrator Toolkit
              </span>
            </div>
            <h4 className="text-base font-bold text-white leading-snug">
              Import & Synchronize Institutional Data
            </h4>
            <p className="text-xs text-[#A1BDD4] leading-relaxed">
              Upload multi-worksheet Excel files, extract student data from scanned PDF memos, or download verified reports.
            </p>
            <div className="pt-2 flex items-center gap-2 flex-wrap">
              <button
                onClick={() => setCurrentTab('excel-import')}
                className="px-3 py-1.5 rounded-xl bg-white text-[#1758A2] text-xs font-semibold hover:bg-slate-50 transition shadow-xs"
              >
                Upload Excel
              </button>
              <button
                onClick={() => setCurrentTab('pdf-upload')}
                className="px-3 py-1.5 rounded-xl bg-[#124580] text-white text-xs font-semibold hover:bg-[#0E3666] transition border border-[#A1BDD4]/30"
              >
                Extract PDF
              </button>
              <button
                onClick={() => setCurrentTab('reports')}
                className="px-3 py-1.5 rounded-xl bg-[#124580] text-white text-xs font-semibold hover:bg-[#0E3666] transition border border-[#A1BDD4]/30"
              >
                Generate Reports
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
