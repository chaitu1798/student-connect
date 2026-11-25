import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Search, Clock } from 'lucide-react';
import { apiClient } from '../../api/client';
import { Internship } from '../../types';

export const InternshipDirectoryPage: React.FC = () => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchInternships = () => {
    setLoading(true);
    let url = `/internships?page_size=20`;
    if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;
    if (categoryFilter) url += `&category=${encodeURIComponent(categoryFilter)}`;

    apiClient.get(url)
      .then((res) => {
        setInternships(res.data.items);
        setTotal(res.data.total);
      })
      .catch((err) => console.error('Error fetching internships:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchInternships();
  }, [categoryFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchInternships();
  };

  return (
    <div className="bg-white min-h-[75vh]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl sm:text-5xl font-semibold tracking-[-0.03em] text-[#1D1D1F]">
            Internships Directory
          </h1>
          <p className="text-sm sm:text-base text-[#6E6E73] mt-2">
            Industry training, corporate projects, and research internships ({total} records).
          </p>
        </div>

        {/* Filter Bar */}
        <form
          onSubmit={handleSearch}
          className="bg-[#F5F5F7] p-3 rounded-3xl grid grid-cols-1 sm:grid-cols-12 gap-2.5"
        >
          <div className="sm:col-span-7 relative">
            <Search className="w-4 h-4 text-[#86868B] absolute left-4 top-3" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by company, student name, or role..."
              className="w-full pl-10 pr-4 py-2.5 bg-white rounded-full text-sm text-[#1D1D1F] placeholder-[#86868B] focus:outline-none focus:ring-2 focus:ring-[#0071E3]/30"
            />
          </div>

          <div className="sm:col-span-3">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full py-2.5 px-4 bg-white rounded-full text-sm text-[#1D1D1F] focus:outline-none focus:ring-2 focus:ring-[#0071E3]/30"
            >
              <option value="">All Categories</option>
              <option value="Technical">Technical</option>
              <option value="Research">Research</option>
              <option value="Corporate">Corporate</option>
              <option value="Government">Government / Public Sector</option>
            </select>
          </div>

          <div className="sm:col-span-2">
            <button
              type="submit"
              className="w-full py-2.5 bg-[#0071E3] hover:bg-[#0077ED] text-white rounded-full text-sm font-medium transition cursor-pointer"
            >
              Search
            </button>
          </div>
        </form>

        {loading && <div className="text-xs text-[#0071E3] font-medium">Loading internships...</div>}

        {/* Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {internships.map((item) => (
            <div
              key={item.id}
              className="bg-[#F5F5F7] hover:bg-[#EFEFF2] p-6 rounded-3xl transition flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-[11px] font-medium px-3 py-1 rounded-full bg-white text-[#1D1D1F]">
                    {item.category || 'Technical'}
                  </span>
                  <span className="text-xs font-mono text-[#6E6E73]">
                    {item.roll_no}
                  </span>
                </div>
                <div>
                  <h3 className="text-base font-semibold text-[#1D1D1F]">{item.organization_name}</h3>
                  <p className="text-xs font-medium text-[#0071E3] mt-0.5">{item.role || 'Intern'}</p>
                </div>
                <div className="text-xs text-[#6E6E73] space-y-1.5 pt-2 border-t border-black/[0.06]">
                  <div className="flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5" />
                    <span>{item.full_name || item.roll_no}</span>
                  </div>
                  {item.organization_district && (
                    <div className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{item.organization_district}</span>
                    </div>
                  )}
                  {item.duration_weeks && (
                    <div className="flex items-center gap-1.5 text-[#1D1D1F] font-medium">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{item.duration_weeks} Weeks</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
