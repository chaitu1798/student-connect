import React, { useState, useEffect } from 'react';
import { Search, ChevronLeft, ChevronRight, ArrowUpRight, ShieldCheck } from 'lucide-react';
import { apiClient } from '../../api/client';

interface StudentDirectoryPageProps {
  setSelectedRollNo: (rollNo: string) => void;
  setCurrentView: (view: string) => void;
}

export const StudentDirectoryPage: React.FC<StudentDirectoryPageProps> = ({
  setSelectedRollNo,
  setCurrentView,
}) => {
  const [students, setStudents] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [yearFilter, setYearFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchStudents = () => {
    setLoading(true);
    let url = `/public/search?page=${page}&page_size=${pageSize}`;
    if (search.trim()) url += `&q=${encodeURIComponent(search.trim())}`;
    if (branchFilter) url += `&branch=${encodeURIComponent(branchFilter)}`;
    if (yearFilter) url += `&year=${encodeURIComponent(yearFilter)}`;

    apiClient.get(url)
      .then((res) => {
        setStudents(res.data.items);
        setTotal(res.data.total);
      })
      .catch((err) => console.error('Error fetching students:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStudents();
  }, [page, branchFilter, yearFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchStudents();
  };

  const handleSelect = (rollNo: string) => {
    setSelectedRollNo(rollNo);
    setCurrentView('student-profile');
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="bg-white min-h-[75vh]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-xs font-medium text-[#0071E3] mb-2">
              <ShieldCheck className="w-4 h-4" />
              <span>Verified Academic Directory</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-semibold tracking-[-0.03em] text-[#1D1D1F]">
              Student Directory
            </h1>
            <p className="text-sm sm:text-base text-[#6E6E73] mt-2">
              Approved student profiles at Vignan's Institute Of Information Technology.
            </p>
          </div>
          <div className="text-xs text-[#6E6E73] bg-[#F5F5F7] px-4 py-2.5 rounded-2xl max-w-xs">
            Personal identity numbers and private contacts are encrypted and shielded by policy.
          </div>
        </div>

        {/* Filter Pill Bar */}
        <form
          onSubmit={handleSearch}
          className="bg-[#F5F5F7] p-3 rounded-3xl grid grid-cols-1 sm:grid-cols-12 gap-2.5"
        >
          <div className="sm:col-span-6 relative">
            <Search className="w-4 h-4 text-[#86868B] absolute left-4 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Roll Number or Full Name..."
              className="w-full pl-10 pr-4 py-2.5 bg-white rounded-full text-sm text-[#1D1D1F] placeholder-[#86868B] focus:outline-none focus:ring-2 focus:ring-[#0071E3]/30"
            />
          </div>

          <div className="sm:col-span-3">
            <select
              value={branchFilter}
              onChange={(e) => {
                setBranchFilter(e.target.value);
                setPage(1);
              }}
              className="w-full py-2.5 px-4 bg-white rounded-full text-sm text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#0071E3]/30"
            >
              <option value="">All Branches</option>
              <option value="Computer Science">Computer Science & Engg</option>
              <option value="Electronics">Electronics & Comm Engg</option>
              <option value="Information Technology">Information Technology</option>
              <option value="Electrical">Electrical & Electronics</option>
              <option value="Mechanical">Mechanical Engineering</option>
              <option value="Civil">Civil Engineering</option>
            </select>
          </div>

          <div className="sm:col-span-2">
            <select
              value={yearFilter}
              onChange={(e) => {
                setYearFilter(e.target.value);
                setPage(1);
              }}
              className="w-full py-2.5 px-4 bg-white rounded-full text-sm text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#0071E3]/30"
            >
              <option value="">Passing Year</option>
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
              <option value="2023">2023</option>
            </select>
          </div>

          <div className="sm:col-span-1">
            <button
              type="submit"
              className="w-full py-2.5 bg-[#0071E3] hover:bg-[#0077ED] text-white rounded-full text-sm font-medium transition cursor-pointer"
            >
              Go
            </button>
          </div>
        </form>

        {/* Results */}
        <div className="bg-[#F5F5F7] rounded-3xl overflow-hidden">
          <div className="px-6 py-4 border-b border-black/[0.06] flex justify-between items-center text-xs text-[#6E6E73]">
            <span>{total} approved student records</span>
            {loading && <span className="text-[#0071E3] font-medium">Updating...</span>}
          </div>

          {students.length > 0 ? (
            <div className="overflow-x-auto bg-white">
              <table className="w-full text-left text-sm">
                <thead className="text-[11px] font-semibold text-[#6E6E73] uppercase tracking-wider border-b border-black/[0.06]">
                  <tr>
                    <th className="px-6 py-4">Student</th>
                    <th className="px-6 py-4">Roll Number</th>
                    <th className="px-6 py-4">Branch</th>
                    <th className="px-6 py-4">Passing Year</th>
                    <th className="px-6 py-4 text-center">Internships</th>
                    <th className="px-6 py-4 text-right">Profile</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-black/[0.05]">
                  {students.map((student) => (
                    <tr
                      key={student.roll_no}
                      onClick={() => handleSelect(student.roll_no)}
                      className="hover:bg-[#F5F5F7]/70 transition cursor-pointer"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full overflow-hidden bg-[#F5F5F7] shrink-0">
                            <img
                              src={`/api/v1/public/photo/${student.roll_no}`}
                              alt={student.full_name}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                (e.target as HTMLElement).style.display = 'none';
                              }}
                            />
                            <div className="w-full h-full flex items-center justify-center bg-[#1D1D1F] text-white font-semibold text-xs -mt-10">
                              {student.full_name?.slice(0, 2).toUpperCase() || 'ST'}
                            </div>
                          </div>
                          <span className="font-semibold text-[#1D1D1F]">{student.full_name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-[#6E6E73]">
                        {student.roll_no}
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs bg-[#F5F5F7] text-[#1D1D1F] px-3 py-1 rounded-full">
                          {student.branch || 'Engineering'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-[#6E6E73] text-xs">
                        {student.ug_year_of_pass || '-'}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <span className="text-xs font-medium text-[#1D1D1F]">
                          {student.internship_count}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center gap-1 text-xs font-medium text-[#0071E3]">
                          View <ArrowUpRight className="w-3.5 h-3.5" />
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-20 space-y-2 bg-white">
              <div className="text-base font-semibold text-[#1D1D1F]">No student profiles found</div>
              <p className="text-xs text-[#6E6E73]">
                Try adjusting your search query or branch filter.
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-black/[0.06] flex items-center justify-between text-xs text-[#6E6E73]">
              <span>Page {page} of {totalPages}</span>
              <div className="flex gap-2">
                <button
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                  className="p-2 rounded-full bg-white border border-black/[0.08] disabled:opacity-40 cursor-pointer"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                  className="p-2 rounded-full bg-white border border-black/[0.08] disabled:opacity-40 cursor-pointer"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
