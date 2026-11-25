import React, { useState, useEffect } from 'react';
import {
  Search,
  ChevronRight,
  CheckCircle2,
  ArrowUpRight,
  Building2,
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { PublicStats } from '../../types';
import { CountUp } from '../../components/ui/CountUp';
import { StudentAvatar } from '../../components/ui/StudentAvatar';

interface HomePageProps {
  setCurrentView: (view: string) => void;
  setSelectedRollNo: (rollNo: string) => void;
}

export const HomePage: React.FC<HomePageProps> = ({ setCurrentView, setSelectedRollNo }) => {
  const [stats, setStats] = useState<PublicStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    apiClient.get('/public/stats')
      .then((res) => setStats(res.data))
      .catch((err) => console.error('Error fetching stats:', err));
  }, []);

  useEffect(() => {
    if (searchQuery.trim().length >= 2) {
      const timer = setTimeout(() => {
        apiClient.get(`/public/suggestions?q=${encodeURIComponent(searchQuery.trim())}`)
          .then((res) => {
            setSuggestions(res.data);
            setShowSuggestions(true);
          })
          .catch(() => setSuggestions([]));
      }, 220);
      return () => clearTimeout(timer);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [searchQuery]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setCurrentView('student-directory');
    }
  };

  const handleSelectStudent = (rollNo: string) => {
    setSelectedRollNo(rollNo);
    setCurrentView('student-profile');
  };

  return (
    <div className="bg-white text-[#1D1D1F] pb-24">
      {/* Apple-Style Hero Section */}
      <section className="pt-16 sm:pt-24 pb-16 px-4 sm:px-6 lg:px-8 text-center max-w-5xl mx-auto">
        <p className="text-xs sm:text-sm font-semibold tracking-wide text-[#6E6E73] mb-3">
          Vignan's Institute Of Information Technology
        </p>
        <h1 className="text-4xl sm:text-6xl lg:text-[64px] font-semibold tracking-[-0.035em] text-[#1D1D1F] leading-[1.06]">
          Student credentials.
          <br />
          <span className="text-[#6E6E73]">Verified at a glance.</span>
        </h1>
        <p className="mt-5 text-base sm:text-xl text-[#6E6E73] max-w-2xl mx-auto font-normal leading-relaxed">
          Explore approved undergraduate profiles, academic records, and verified corporate internships across every engineering discipline.
        </p>

        {/* Pill Search Bar */}
        <div className="max-w-xl mx-auto mt-9 relative">
          <form
            onSubmit={handleSearchSubmit}
            className="flex items-center bg-[#F5F5F7] border border-black/[0.06] rounded-full px-4 py-2 focus-within:bg-white focus-within:ring-4 focus-within:ring-[#0071E3]/15 transition-all"
          >
            <Search className="w-4 h-4 text-[#86868B] shrink-0 ml-1" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onFocus={() => searchQuery.trim().length >= 2 && setShowSuggestions(true)}
              placeholder="Search by Roll No or Student Name..."
              className="w-full bg-transparent px-3 py-2 text-sm text-[#1D1D1F] placeholder-[#86868B] focus:outline-none"
            />
            <button
              type="submit"
              className="bg-[#0071E3] hover:bg-[#0077ED] text-white text-xs font-medium px-5 py-2 rounded-full transition shrink-0 cursor-pointer"
            >
              Search
            </button>
          </form>

          {/* Suggestions Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute left-0 right-0 top-full mt-2 bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl border border-black/[0.08] text-left z-30 overflow-hidden divide-y divide-black/[0.05]">
              {suggestions.map((item) => (
                <button
                  key={item.roll_no}
                  type="button"
                  onClick={() => handleSelectStudent(item.roll_no)}
                  className="w-full px-5 py-3.5 hover:bg-[#F5F5F7] flex items-center justify-between text-left transition cursor-pointer"
                >
                  <div>
                    <div className="text-sm font-semibold text-[#1D1D1F]">{item.full_name}</div>
                    <div className="text-xs text-[#6E6E73] font-mono mt-0.5">
                      {item.roll_no} · {item.branch}
                    </div>
                  </div>
                  <span className="text-xs text-[#0071E3] font-medium inline-flex items-center gap-0.5">
                    View <ChevronRight className="w-3.5 h-3.5" />
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Hero CTAs */}
        <div className="mt-7 flex flex-wrap items-center justify-center gap-4">
          <button
            onClick={() => setCurrentView('student-directory')}
            className="px-6 py-2.5 bg-[#0071E3] hover:bg-[#0077ED] text-white rounded-full text-sm font-medium transition cursor-pointer"
          >
            Explore Student Directory
          </button>
          <button
            onClick={() => setCurrentView('internship-directory')}
            className="inline-flex items-center gap-1 text-sm font-medium text-[#0071E3] hover:underline px-3 py-2 cursor-pointer"
          >
            <span>Browse Internships</span>
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        <div className="mt-6 flex flex-wrap justify-center gap-2 text-xs text-[#86868B]">
          <span>Quick lookup:</span>
          <button onClick={() => handleSelectStudent('21A91A0501')} className="text-[#0071E3] hover:underline cursor-pointer">
            21A91A0501
          </button>
          <span>·</span>
          <button onClick={() => handleSelectStudent('21A91A0502')} className="text-[#0071E3] hover:underline cursor-pointer">
            21A91A0502
          </button>
        </div>
      </section>

      {/* Metrics Bento Strip */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mb-12">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          <div className="bg-[#F5F5F7] rounded-3xl p-7">
            <div className="text-3xl sm:text-4xl font-semibold tracking-tight text-[#1D1D1F] tabular-nums">
              <CountUp to={stats?.total_students ?? 0} duration={800} />
            </div>
            <div className="text-xs font-medium text-[#6E6E73] mt-2">
              Registered Students
            </div>
          </div>

          <div className="bg-[#F5F5F7] rounded-3xl p-7">
            <div className="text-3xl sm:text-4xl font-semibold tracking-tight text-[#1D1D1F] tabular-nums">
              <CountUp to={stats?.total_internships ?? 0} duration={800} />
            </div>
            <div className="text-xs font-medium text-[#6E6E73] mt-2">
              Internship Records
            </div>
          </div>

          <div className="bg-[#F5F5F7] rounded-3xl p-7">
            <div className="text-3xl sm:text-4xl font-semibold tracking-tight text-[#1D1D1F] tabular-nums">
              <CountUp to={stats?.total_branches ?? 7} duration={800} />
            </div>
            <div className="text-xs font-medium text-[#6E6E73] mt-2">
              Academic Branches
            </div>
          </div>

          <div className="bg-[#F5F5F7] rounded-3xl p-7">
            <div className="text-3xl sm:text-4xl font-semibold tracking-tight text-[#0071E3] tabular-nums">
              <CountUp to={100} suffix="%" duration={800} />
            </div>
            <div className="text-xs font-medium text-[#6E6E73] mt-2">
              Verified Integrity
            </div>
          </div>
        </div>
      </section>

      {/* Dark Apple Hardware-Style Showcase: Departmental Distribution */}
      {stats?.branch_statistics && Object.keys(stats.branch_statistics).length > 0 && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 mb-16">
          <div className="bg-[#000000] text-white rounded-[32px] p-8 sm:p-12">
            <div className="max-w-2xl mb-10">
              <p className="text-xs font-semibold uppercase tracking-widest text-[#86868B] mb-2">
                Academic Architecture
              </p>
              <h2 className="text-3xl sm:text-4xl font-semibold tracking-[-0.025em] leading-tight">
                Every department. One unified record.
              </h2>
              <p className="text-sm sm:text-base text-[#86868B] mt-3">
                Live distribution of enrolled engineering cohorts across Vignan's Institute Of Information Technology.
              </p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3.5">
              {Object.entries(stats.branch_statistics).map(([branch, count]) => (
                <div
                  key={branch}
                  className="p-5 rounded-2xl bg-white/[0.06] border border-white/[0.08] hover:bg-white/[0.1] transition"
                >
                  <div className="text-xs text-[#A1A1A6] truncate">{branch}</div>
                  <div className="text-2xl sm:text-3xl font-semibold text-white mt-2 tabular-nums">
                    {count}
                  </div>
                  <div className="text-[11px] text-[#6E6E73] mt-1">Enrolled students</div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Recently Approved Profiles & Internship Highlights */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Approved Student Profiles */}
          <div className="lg:col-span-8 space-y-5">
            <div className="flex items-end justify-between">
              <div>
                <h2 className="text-2xl sm:text-3xl font-semibold tracking-[-0.02em] text-[#1D1D1F]">
                  Approved Student Profiles
                </h2>
                <p className="text-sm text-[#6E6E73] mt-1">
                  Publicly verifiable academic credentials.
                </p>
              </div>
              <button
                onClick={() => setCurrentView('student-directory')}
                className="text-xs sm:text-sm font-medium text-[#0071E3] hover:underline inline-flex items-center gap-0.5 cursor-pointer shrink-0"
              >
                <span>See all</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {stats?.recent_approved_profiles && stats.recent_approved_profiles.length > 0 ? (
                stats.recent_approved_profiles.map((student) => (
                  <div
                    key={student.roll_no}
                    onClick={() => handleSelectStudent(student.roll_no)}
                    className="group bg-[#F5F5F7] hover:bg-[#EFEFF2] rounded-3xl p-6 transition cursor-pointer flex flex-col justify-between"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-3 min-w-0">
                          <StudentAvatar
                            rollNo={student.roll_no}
                            name={student.full_name}
                            size="md"
                          />
                          <div className="min-w-0">
                            <h3 className="text-base font-semibold text-[#1D1D1F] truncate">
                              {student.full_name}
                            </h3>
                            <div className="text-xs font-mono text-[#6E6E73]">
                              {student.roll_no}
                            </div>
                          </div>
                        </div>
                        <CheckCircle2 className="w-4 h-4 text-[#0071E3] shrink-0 mt-1" />
                      </div>

                      <div className="mt-4 pt-4 border-t border-black/[0.06] flex items-center justify-between text-xs text-[#6E6E73]">
                        <span className="truncate">{student.branch}</span>
                        <span className="shrink-0 font-medium text-[#1D1D1F]">
                          {student.internship_count} Internships
                        </span>
                      </div>
                    </div>

                    <div className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-[#0071E3] group-hover:underline">
                      <span>View profile</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 bg-[#F5F5F7] rounded-3xl p-10 text-center text-sm text-[#6E6E73]">
                  No public profiles approved yet.
                </div>
              )}
            </div>
          </div>

          {/* Top Organizations */}
          <div className="lg:col-span-4 space-y-5">
            <div>
              <h2 className="text-2xl sm:text-3xl font-semibold tracking-[-0.02em] text-[#1D1D1F]">
                Top Partners
              </h2>
              <p className="text-sm text-[#6E6E73] mt-1">
                Organizations engaging our cohorts.
              </p>
            </div>

            <div className="bg-[#F5F5F7] rounded-3xl p-6 space-y-3">
              {stats?.internship_highlights && stats.internship_highlights.length > 0 ? (
                stats.internship_highlights.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3.5 rounded-2xl bg-white border border-black/[0.04]"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="w-8 h-8 rounded-full bg-[#F5F5F7] text-[#1D1D1F] flex items-center justify-center shrink-0">
                        <Building2 className="w-4 h-4" />
                      </div>
                      <span className="text-xs font-semibold text-[#1D1D1F] truncate">
                        {item.organization}
                      </span>
                    </div>
                    <span className="text-xs font-medium text-[#6E6E73] shrink-0 ml-2">
                      {item.count} offers
                    </span>
                  </div>
                ))
              ) : (
                <div className="py-8 text-center text-xs text-[#6E6E73]">
                  No internship records available.
                </div>
              )}

              <button
                onClick={() => setCurrentView('internship-directory')}
                className="w-full mt-2 py-2.5 bg-[#1D1D1F] hover:bg-black text-white rounded-full text-xs font-medium transition cursor-pointer"
              >
                Explore All Internships
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
