import React, { useState, useEffect } from 'react';
import {
  Briefcase,
  Search,
  Plus,
  Edit3,
  Trash2,
  Upload,
  Download,
  FileCheck2,
  X,
  Clock,
  MapPin,
  Building2,
  Calendar,
  Eye,
  DollarSign,
  Award,
  Filter,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  ExternalLink,
  UserCheck
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { Internship, InternshipStats } from '../../types';
import { TactileButton } from '../../components/ui/TactileButton';
import { SpotlightCard } from '../../components/ui/SpotlightCard';
import { CountUp } from '../../components/ui/CountUp';

export const InternshipsManager: React.FC<{ isAdmin?: boolean }> = ({ isAdmin }) => {
  const [internships, setInternships] = useState<Internship[]>([]);
  const [stats, setStats] = useState<InternshipStats | null>(null);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  // Filters
  const [search, setSearch] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [districtFilter, setDistrictFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [modeFilter, setModeFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [certFilter, setCertFilter] = useState('');
  const [loading, setLoading] = useState(false);

  // View Details Modal
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [selectedInternship, setSelectedInternship] = useState<Internship | null>(null);

  // Modal Add / Edit
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState<Partial<Internship>>({});
  const [saving, setSaving] = useState(false);

  // Certificate upload
  const [certModalOpen, setCertModalOpen] = useState(false);
  const [certTargetId, setCertTargetId] = useState<string | number | null>(null);
  const [certFile, setCertFile] = useState<File | null>(null);
  const [uploadingCert, setUploadingCert] = useState(false);

  const fetchStats = () => {
    apiClient.get('/internships/statistics')
      .then((res) => setStats(res.data))
      .catch((err) => console.error('Error fetching internship statistics:', err));
  };

  const fetchInternships = () => {
    setLoading(true);
    let url = `/internships?page=${page}&page_size=${pageSize}`;
    if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;
    if (branchFilter.trim()) url += `&branch=${encodeURIComponent(branchFilter.trim())}`;
    if (districtFilter.trim()) url += `&district=${encodeURIComponent(districtFilter.trim())}`;
    if (categoryFilter) url += `&category=${encodeURIComponent(categoryFilter)}`;
    if (modeFilter) url += `&mode=${encodeURIComponent(modeFilter)}`;
    if (typeFilter) url += `&type=${encodeURIComponent(typeFilter)}`;
    if (certFilter) url += `&certificate_status=${encodeURIComponent(certFilter)}`;

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
  }, [page, branchFilter, districtFilter, categoryFilter, modeFilter, typeFilter, certFilter]);

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const openId = params.get('open_details');
    if (openId && internships.length > 0) {
      const match = internships.find(i => String(i.id) === openId) || internships[0];
      if (match) {
        setSelectedInternship(match);
        setViewModalOpen(true);
      }
    }
  }, [internships]);

  const handleResetFilters = () => {
    setSearch('');
    setBranchFilter('');
    setDistrictFilter('');
    setCategoryFilter('');
    setModeFilter('');
    setTypeFilter('');
    setCertFilter('');
    setPage(1);
    // Directly fetch with clean params
    setLoading(true);
    apiClient.get(`/internships?page=1&page_size=${pageSize}`)
      .then((res) => {
        setInternships(res.data.items);
        setTotal(res.data.total);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchInternships();
  };

  // Auto calculate duration in weeks when start and end dates change
  const handleDateChange = (field: 'start_date' | 'end_date', val: string) => {
    const updated = { ...formData, [field]: val };
    if (updated.start_date && updated.end_date) {
      const start = new Date(updated.start_date);
      const end = new Date(updated.end_date);
      const diffTime = end.getTime() - start.getTime();
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      if (diffDays > 0) {
        updated.duration_weeks = Math.max(1, Math.round(diffDays / 7));
      }
    }
    setFormData(updated);
  };

  const handleOpenAdd = () => {
    setFormData({
      roll_no: '',
      full_name: '',
      branch: 'CSE',
      name_of_college: "Vignan's Institute Of Information Technology",
      organization_name: '',
      organization_district: 'Hyderabad',
      organization_address: '',
      category: 'Technical',
      role: 'Software Intern',
      mode: 'Offline',
      internship_type: 'Paid',
      stipend_amount: 15000,
      stipend_range: '10k - 20k',
      certificate_received: 'No',
      regular_internship: 'Regular',
      offered_by: 'Campus Drive',
      gender: 'Male',
      contact_no: ''
    });
    setEditMode(false);
    setModalOpen(true);
  };

  const handleOpenEdit = (item: Internship) => {
    setFormData({
      ...item,
      organization_name: item.organization_name || item.name_of_organization || '',
      mode: item.mode || item.mode_of_internship || 'Offline',
      name_of_college: item.name_of_college || item.college_name || '',
      offered_by: item.offered_by || item.internship_offered_by || '',
      contact_no: item.contact_no || item.contact_number || ''
    });
    setEditMode(true);
    setModalOpen(true);
  };

  const handleOpenView = (item: Internship) => {
    setSelectedInternship(item);
    setViewModalOpen(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editMode && formData.id) {
        await apiClient.put(`/internships/${formData.id}`, formData);
      } else {
        await apiClient.post('/internships', formData);
      }
      setModalOpen(false);
      fetchInternships();
      fetchStats();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save internship record.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string | number) => {
    if (!confirm('Are you sure you want to permanently delete this internship record? This action will be audited.')) return;
    try {
      await apiClient.delete(`/internships/${id}`);
      fetchInternships();
      fetchStats();
      if (viewModalOpen && selectedInternship?.id === id) {
        setViewModalOpen(false);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete record.');
    }
  };

  const handleUploadCertSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!certTargetId || !certFile) return;

    setUploadingCert(true);
    const fd = new FormData();
    fd.append('file', certFile);

    try {
      await apiClient.post(`/documents/internship/${certTargetId}/certificate`, fd);
      alert('Certificate uploaded and verified successfully!');
      setCertModalOpen(false);
      setCertFile(null);
      fetchInternships();
      fetchStats();
      if (viewModalOpen && selectedInternship?.id === certTargetId) {
        // Refresh selected internship
        apiClient.get(`/internships/${certTargetId}`).then(res => setSelectedInternship(res.data));
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Certificate upload failed.');
    } finally {
      setUploadingCert(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize);
  const hasActiveFilters = Boolean(search || branchFilter || districtFilter || categoryFilter || modeFilter || typeFilter || certFilter);

  return (
    <div className="space-y-6">
      {/* Page Title Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
        <div>
          <div className="flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-[#1758A2]" />
            <h1 className="text-xl sm:text-2xl font-bold text-[#16283B]">Internship & Placement Records</h1>
          </div>
          <p className="text-xs text-[#64748B] mt-1">
            Tracking corporate, technical, research & virtual internships with full 22-attribute institutional validation.
          </p>
        </div>
        <button
          onClick={handleOpenAdd}
          className="asseto-btn-primary text-xs py-2 px-4 rounded-xl"
        >
          <Plus className="w-4 h-4 text-white" />
          <span>Add Internship Record</span>
        </button>
      </div>

      {/* Real Statistics Ribbon */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 border border-[#E8ECEF] rounded-2xl bg-white shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
            <div className="flex items-center justify-between text-[#64748B] mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Total Internships</span>
              <Briefcase className="w-4 h-4 text-[#1758A2]" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-[#16283B]">
              <CountUp to={stats.total} />
            </div>
            <p className="text-[11px] text-[#64748B] mt-1">Across all academic engineering branches</p>
          </div>

          <div className="p-5 border border-[#E8ECEF] rounded-2xl bg-white shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
            <div className="flex items-center justify-between text-[#64748B] mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Partner Companies</span>
              <Building2 className="w-4 h-4 text-[#1758A2]" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-[#16283B]">
              <CountUp to={stats.total_organizations} />
            </div>
            <p className="text-[11px] text-[#64748B] mt-1">Across {stats.district_wise.length} industrial districts</p>
          </div>

          <div className="p-5 border border-[#E8ECEF] rounded-2xl bg-white shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
            <div className="flex items-center justify-between text-[#64748B] mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Certificate Status</span>
              <Award className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl lg:text-3xl font-bold text-emerald-600">
                {stats.certificate_status.received_percentage}%
              </span>
              <span className="text-xs text-[#64748B] font-medium">
                ({stats.certificate_status.received} / {stats.total} verified)
              </span>
            </div>
            <p className="text-[11px] text-[#64748B] mt-1">{stats.certificate_status.pending} pending verification</p>
          </div>

          <div className="p-5 border border-[#E8ECEF] rounded-2xl bg-white shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
            <div className="flex items-center justify-between text-[#64748B] mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider">Average Stipend</span>
              <DollarSign className="w-4 h-4 text-[#1758A2]" />
            </div>
            <div className="text-2xl lg:text-3xl font-bold text-[#16283B]">
              ₹{Math.round(stats.stipend_stats.avg_stipend).toLocaleString()}
              <span className="text-xs font-normal text-[#64748B]">/mo</span>
            </div>
            <p className="text-[11px] text-[#64748B] mt-1">
              Max ₹{Math.round(stats.stipend_stats.max_stipend).toLocaleString()} • {stats.stipend_stats.paid_count} paid roles
            </p>
          </div>
        </div>
      )}

      {/* Advanced Filter Bar (7 Dimensions) */}
      <div className="bg-white p-5 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by company name, student roll number, candidate name, or designation..."
              className="w-full pl-9 pr-3 py-2 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] focus:bg-white focus:border-[#1758A2] outline-none text-[#16283B]"
            />
          </div>
          <button
            type="submit"
            className="asseto-btn-primary text-xs py-2 px-4 rounded-xl"
          >
            Search
          </button>
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleResetFilters}
              className="asseto-btn-secondary text-xs py-2 px-3 rounded-xl flex items-center gap-1.5"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </form>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 pt-1">
          {/* Branch filter */}
          <div>
            <label className="block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Branch</label>
            <select
              value={branchFilter}
              onChange={(e) => { setBranchFilter(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] text-[#16283B]"
            >
              <option value="">All Branches</option>
              <option value="CSE">CSE</option>
              <option value="ECE">ECE</option>
              <option value="IT">IT</option>
              <option value="EEE">EEE</option>
              <option value="MECH">MECH</option>
              <option value="CIVIL">CIVIL</option>
              <option value="AI_DS">AI & DS</option>
            </select>
          </div>

          {/* District filter */}
          <div>
            <label className="block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">District</label>
            <input
              type="text"
              value={districtFilter}
              onChange={(e) => { setDistrictFilter(e.target.value); setPage(1); }}
              placeholder="e.g. Hyderabad"
              className="w-full py-1.5 px-2.5 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] text-[#16283B]"
            />
          </div>

          {/* Category filter */}
          <div>
            <label className="block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] text-[#16283B]"
            >
              <option value="">All Categories</option>
              <option value="Technical">Technical</option>
              <option value="Research">Research</option>
              <option value="Corporate">Corporate</option>
              <option value="Government">Government</option>
              <option value="NGO">NGO</option>
            </select>
          </div>

          {/* Mode filter */}
          <div>
            <label className="block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Mode</label>
            <select
              value={modeFilter}
              onChange={(e) => { setModeFilter(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] text-[#16283B]"
            >
              <option value="">All Modes</option>
              <option value="Offline">Offline</option>
              <option value="Online">Online / Virtual</option>
              <option value="Hybrid">Hybrid</option>
            </select>
          </div>

          {/* Type filter */}
          <div>
            <label className="block text-[11px] font-semibold text-[#64748B] uppercase tracking-wider mb-1">Type</label>
            <select
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 border border-[#E8ECEF] rounded-xl text-xs bg-[#F6F6F6] text-[#16283B]"
            >
              <option value="">All Types</option>
              <option value="Paid">Paid</option>
              <option value="Unpaid">Unpaid</option>
            </select>
          </div>

          {/* Certificate filter */}
          <div>
            <label className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-1">Certificate</label>
            <select
              value={certFilter}
              onChange={(e) => { setCertFilter(e.target.value); setPage(1); }}
              className="w-full py-1.5 px-2.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
            >
              <option value="">All Statuses</option>
              <option value="Yes">Received</option>
              <option value="No">Pending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Internships Table */}
      <div className="bg-white rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-[#16283B]">
            <thead className="bg-[#F8FAFC] text-[11px] font-semibold text-[#64748B] uppercase tracking-wider border-b border-[#E8ECEF]">
              <tr>
                <th className="px-5 py-3.5">Candidate</th>
                <th className="px-5 py-3.5">Organization & District</th>
                <th className="px-5 py-3.5">Role & Category</th>
                <th className="px-5 py-3.5">Mode / Type</th>
                <th className="px-5 py-3.5">Duration</th>
                <th className="px-5 py-3.5">Stipend</th>
                <th className="px-5 py-3.5 text-center">Certificate</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F4F7]">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-[#64748B]">
                    <div className="w-8 h-8 border-2 border-[#1758A2] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <span>Loading internship records...</span>
                  </td>
                </tr>
              ) : internships.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-12 text-center text-[#64748B]">
                    <Briefcase className="w-8 h-8 text-[#94A3B8] mx-auto mb-2 opacity-50" />
                    <p className="font-semibold text-sm text-[#16283B]">No internship records found</p>
                    <p className="text-xs text-[#64748B] mt-1">Try resetting filters or record a new internship above.</p>
                  </td>
                </tr>
              ) : (
                internships.map((item) => (
                  <tr key={item.id} className="hover:bg-[#F8FAFC] transition">
                    <td className="px-5 py-4">
                      <span className="font-mono font-bold text-[#1758A2] block">
                        {item.roll_no}
                      </span>
                      <span className="text-xs font-semibold text-[#16283B] block">
                        {item.full_name || 'Student Name N/A'}
                      </span>
                      {item.branch && (
                        <span className="inline-block px-1.5 py-0.5 rounded text-[10px] bg-slate-100 font-mono text-[#64748B] mt-0.5">
                          {item.branch}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4">
                      <span className="font-bold text-[#16283B] block">
                        {item.organization_name || item.name_of_organization}
                      </span>
                      <span className="text-xs text-[#64748B] flex items-center gap-1 mt-0.5">
                        <MapPin className="w-3 h-3 text-[#94A3B8] inline" />
                        {item.organization_district || 'District N/A'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-xs font-medium">
                      <span className="font-semibold text-[#16283B] block">{item.role || 'Intern'}</span>
                      <span className="text-[#64748B]">{item.category || 'General'}</span>
                    </td>
                    <td className="px-5 py-4 text-xs">
                      <span className="font-semibold text-[#16283B]">{item.mode || item.mode_of_internship || 'Offline'}</span>
                      <span className="text-[#64748B] block">{item.internship_type || 'Paid'}</span>
                    </td>
                    <td className="px-5 py-4 text-xs font-mono">
                      {item.duration_weeks ? (
                        <span className="font-semibold text-[#1758A2]">{item.duration_weeks} wks</span>
                      ) : (
                        <span className="text-[#94A3B8]">-</span>
                      )}
                      {item.start_date && (
                        <span className="block text-[11px] text-[#64748B]">
                          {item.start_date}
                        </span>
                      )}
                    </td>
                    <td className="px-5 py-4 text-xs font-semibold text-emerald-700 font-mono">
                      {item.stipend_amount && item.stipend_amount > 0
                        ? `₹${item.stipend_amount.toLocaleString()}/mo`
                        : <span className="text-[#94A3B8] font-normal">Unpaid</span>}
                    </td>
                    <td className="px-5 py-4 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${item.certificate_received === 'Yes'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-amber-50 text-amber-700 border border-amber-200'
                        }`}>
                        {item.certificate_received === 'Yes' ? (
                          <>
                            <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                            Received
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-3 h-3 text-amber-600" />
                            Pending
                          </>
                        )}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right space-x-1 whitespace-nowrap">
                      {/* View Details Modal Trigger */}
                      <button
                        onClick={() => handleOpenView(item)}
                        className="p-1.5 text-[#64748B] hover:text-[#1758A2] hover:bg-[#1758A2]/10 rounded-lg transition"
                        title="View Full 22 Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>

                      {/* Upload Certificate */}
                      <button
                        onClick={() => {
                          setCertTargetId(item.id!);
                          setCertModalOpen(true);
                        }}
                        className="p-1.5 text-slate-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition"
                        title="Upload Certificate Document"
                      >
                        <Upload className="w-4 h-4" />
                      </button>

                      {/* Download Certificate */}
                      {(item.certificate_file_path || item.certificate_path) && (
                        <a
                          href={`/api/v1/documents/download?path=${encodeURIComponent(item.certificate_file_path || item.certificate_path || '')}`}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-block p-1.5 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition"
                          title="Download Verified Certificate"
                        >
                          <Download className="w-4 h-4" />
                        </a>
                      )}

                      {/* Edit Record */}
                      <button
                        onClick={() => handleOpenEdit(item)}
                        className="p-1.5 text-slate-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition"
                        title="Edit Internship Record"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>

                      {/* Delete Record */}
                      <button
                        onClick={() => item.id && handleDelete(item.id)}
                        className="p-1.5 text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                        title="Delete Internship Record"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        {totalPages > 1 && (
          <div className="p-4 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600 bg-slate-50/50">
            <div>
              Showing page <span className="font-semibold text-slate-900">{page}</span> of{' '}
              <span className="font-semibold text-slate-900">{totalPages}</span> ({total} total records)
            </div>
            <div className="flex space-x-2">
              <TactileButton
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="rounded-lg text-xs"
              >
                Previous
              </TactileButton>
              <TactileButton
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
                className="rounded-lg text-xs"
              >
                Next
              </TactileButton>
            </div>
          </div>
        )}
      </div>

      {/* 1. DEDICATED FULL INTERNSHIP DETAILS MODAL (22 Attributes) */}
      {viewModalOpen && selectedInternship && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[92vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden my-auto">
            {/* Modal Header */}
            <div className="bg-slate-900 text-white p-6 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-indigo-500/30 text-indigo-200 border border-indigo-400/30">
                    {selectedInternship.roll_no}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-semibold ${selectedInternship.certificate_received === 'Yes'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                    {selectedInternship.certificate_received === 'Yes' ? 'Certificate Verified' : 'Certificate Pending'}
                  </span>
                </div>
                <h2 className="text-xl font-bold font-serif text-white">
                  {selectedInternship.organization_name || selectedInternship.name_of_organization}
                </h2>
                <p className="text-xs text-slate-300 mt-0.5">
                  {selectedInternship.role || 'Intern'} • {selectedInternship.category || 'Technical'} • {selectedInternship.mode || selectedInternship.mode_of_internship || 'Offline'}
                </p>
              </div>
              <button
                onClick={() => setViewModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content - Structured Institutional Sections */}
            <div className="flex-1 overflow-y-auto p-6 space-y-5 text-sm bg-slate-50/50">
              {/* Section 1: Candidate & College */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                  Candidate & Institution Information
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Roll Number:</span>
                    <span className="font-mono font-bold text-slate-900">{selectedInternship.roll_no}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Student Name:</span>
                    <span className="font-semibold text-slate-900">{selectedInternship.full_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Branch:</span>
                    <span className="font-medium text-slate-900">{selectedInternship.branch || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">College Name:</span>
                    <span className="text-slate-800">{selectedInternship.name_of_college || selectedInternship.college_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Gender:</span>
                    <span className="text-slate-800">{selectedInternship.gender || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Contact Number:</span>
                    <span className="font-mono text-slate-800">{selectedInternship.contact_no || selectedInternship.contact_number || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Section 2: Organization & Location */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Building2 className="w-3.5 h-3.5 text-indigo-600" />
                  Organization & Facility Details
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Organization Name:</span>
                    <span className="font-semibold text-slate-900">
                      {selectedInternship.organization_name || selectedInternship.name_of_organization}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Organization District:</span>
                    <span className="text-slate-800 font-medium">
                      {selectedInternship.organization_district || 'N/A'}
                    </span>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-slate-400 block">Office / Facility Address:</span>
                    <span className="text-slate-800">
                      {selectedInternship.organization_address || 'Address not recorded.'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Section 3: Role, Modality & Institutional Offer */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-indigo-600" />
                  Role, Modality & Institutional Classification
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Designation / Role:</span>
                    <span className="font-semibold text-slate-900">{selectedInternship.role || 'Intern'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Category:</span>
                    <span className="text-slate-800">{selectedInternship.category || 'Technical'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Mode of Internship:</span>
                    <span className="text-slate-800 font-semibold">{selectedInternship.mode || selectedInternship.mode_of_internship || 'Offline'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Internship Type:</span>
                    <span className="text-slate-800 font-semibold">{selectedInternship.internship_type || 'Paid'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Offered By:</span>
                    <span className="text-slate-800">{selectedInternship.offered_by || selectedInternship.internship_offered_by || 'On-Campus Drive'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Track (Regular/AEP/IDEA LAB):</span>
                    <span className="text-slate-800">{selectedInternship.regular_internship || 'Regular'}</span>
                  </div>
                </div>
              </div>

              {/* Section 4: Timeline & Compensation */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5 text-indigo-600" />
                  Timeline & Financial Compensation
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 block">Start Date:</span>
                    <span className="font-mono text-slate-900 font-medium">{selectedInternship.start_date || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">End Date:</span>
                    <span className="font-mono text-slate-900 font-medium">{selectedInternship.end_date || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Duration (Weeks):</span>
                    <span className="font-mono font-bold text-indigo-700">
                      {selectedInternship.duration_weeks ? `${selectedInternship.duration_weeks} Weeks` : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block">Stipend Amount:</span>
                    <span className="font-mono font-bold text-emerald-700">
                      {selectedInternship.stipend_amount
                        ? `₹${selectedInternship.stipend_amount.toLocaleString()}/mo`
                        : 'Unpaid'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Section 5: Certificate Document & Audit */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Award className="w-3.5 h-3.5 text-indigo-600" />
                    Verified Completion Certificate
                  </h4>
                  <p className="text-xs text-slate-600">
                    Status:{' '}
                    <span className={`font-semibold ${selectedInternship.certificate_received === 'Yes' ? 'text-emerald-700' : 'text-amber-700'}`}>
                      {selectedInternship.certificate_received === 'Yes' ? 'Received & Confirmed' : 'Pending Verification'}
                    </span>
                    {(selectedInternship.certificate_file_path || selectedInternship.certificate_path) && (
                      <span className="text-slate-400 ml-2 font-mono text-[11px]">
                        (Attached document on disk)
                      </span>
                    )}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <TactileButton
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setCertTargetId(selectedInternship.id!);
                      setCertModalOpen(true);
                    }}
                    icon={<Upload className="w-3.5 h-3.5" />}
                    className="rounded-xl text-xs"
                  >
                    Upload / Replace
                  </TactileButton>
                  {(selectedInternship.certificate_file_path || selectedInternship.certificate_path) && (
                    <a
                      href={`/api/v1/documents/download?path=${encodeURIComponent(selectedInternship.certificate_file_path || selectedInternship.certificate_path || '')}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <TactileButton
                        variant="primary"
                        size="sm"
                        icon={<Download className="w-3.5 h-3.5 text-white" />}
                        className="bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs"
                      >
                        Download Certificate
                      </TactileButton>
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-200 bg-white flex justify-between items-center">
              <TactileButton
                variant="outline"
                size="sm"
                onClick={() => selectedInternship.id && handleDelete(selectedInternship.id)}
                icon={<Trash2 className="w-4 h-4 text-red-600" />}
                className="text-red-600 hover:bg-red-50 rounded-xl text-xs border-red-200"
              >
                Delete Record
              </TactileButton>
              <div className="flex gap-2">
                <TactileButton
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    handleOpenEdit(selectedInternship);
                    setViewModalOpen(false);
                  }}
                  icon={<Edit3 className="w-4 h-4" />}
                  className="rounded-xl text-xs"
                >
                  Edit Record
                </TactileButton>
                <TactileButton
                  variant="primary"
                  size="sm"
                  onClick={() => setViewModalOpen(false)}
                  className="bg-slate-900 text-white rounded-xl text-xs"
                >
                  Close
                </TactileButton>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. MODAL ADD / EDIT INTERNSHIP (All 22 attributes) */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] shadow-2xl border border-slate-200 flex flex-col overflow-hidden my-auto">
            <div className="bg-slate-900 text-white p-5 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold font-serif">
                  {editMode ? 'Edit Internship Record' : 'Record New Internship'}
                </h3>
                <p className="text-xs text-slate-300">
                  Full corporate placement and training details (all 22 attributes supported)
                </p>
              </div>
              <button onClick={() => setModalOpen(false)} className="text-slate-400 hover:text-white p-1">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Student Roll No *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.roll_no || ''}
                    onChange={(e) => setFormData({ ...formData, roll_no: e.target.value.toUpperCase() })}
                    placeholder="e.g. 21A91A0501"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Candidate Full Name
                  </label>
                  <input
                    type="text"
                    value={formData.full_name || ''}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    placeholder="Candidate name as per records"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Branch
                  </label>
                  <select
                    value={formData.branch || 'CSE'}
                    onChange={(e) => setFormData({ ...formData, branch: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                  >
                    <option value="CSE">CSE</option>
                    <option value="ECE">ECE</option>
                    <option value="IT">IT</option>
                    <option value="EEE">EEE</option>
                    <option value="MECH">MECH</option>
                    <option value="CIVIL">CIVIL</option>
                    <option value="AI_DS">AI & DS</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    College Name
                  </label>
                  <input
                    type="text"
                    value={formData.name_of_college || formData.college_name || ''}
                    onChange={(e) => setFormData({ ...formData, name_of_college: e.target.value, college_name: e.target.value })}
                    placeholder="e.g. Vignan's Institute Of Information Technology"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Organization Name (Internship) *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.organization_name || formData.name_of_organization || ''}
                    onChange={(e) => setFormData({ ...formData, organization_name: e.target.value, name_of_organization: e.target.value })}
                    placeholder="e.g. Microsoft India, Amazon"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Role / Designation
                  </label>
                  <input
                    type="text"
                    value={formData.role || ''}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    placeholder="e.g. Software Engineer Intern"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Organization District
                  </label>
                  <input
                    type="text"
                    value={formData.organization_district || ''}
                    onChange={(e) => setFormData({ ...formData, organization_district: e.target.value })}
                    placeholder="e.g. Hyderabad, Bengaluru"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Category</label>
                  <select
                    value={formData.category || 'Technical'}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                  >
                    <option value="Technical">Technical</option>
                    <option value="Research">Research</option>
                    <option value="Corporate">Corporate</option>
                    <option value="Government">Government</option>
                    <option value="NGO">NGO</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Mode of Internship</label>
                  <select
                    value={formData.mode || formData.mode_of_internship || 'Offline'}
                    onChange={(e) => setFormData({ ...formData, mode: e.target.value, mode_of_internship: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                  >
                    <option value="Offline">Offline</option>
                    <option value="Online">Online / Virtual</option>
                    <option value="Hybrid">Hybrid</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Internship Type</label>
                  <select
                    value={formData.internship_type || 'Paid'}
                    onChange={(e) => setFormData({ ...formData, internship_type: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                  >
                    <option value="Paid">Paid</option>
                    <option value="Unpaid">Unpaid</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Stipend (₹/Month)</label>
                  <input
                    type="number"
                    value={formData.stipend_amount ?? ''}
                    onChange={(e) => setFormData({ ...formData, stipend_amount: parseFloat(e.target.value) || 0 })}
                    placeholder="e.g. 25000"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Stipend Range</label>
                  <input
                    type="text"
                    value={formData.stipend_range || ''}
                    onChange={(e) => setFormData({ ...formData, stipend_range: e.target.value })}
                    placeholder="e.g. 20k - 30k"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Start Date</label>
                  <input
                    type="date"
                    value={formData.start_date || ''}
                    onChange={(e) => handleDateChange('start_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">End Date</label>
                  <input
                    type="date"
                    value={formData.end_date || ''}
                    onChange={(e) => handleDateChange('end_date', e.target.value)}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">
                    Duration (Weeks) - Auto Calculated
                  </label>
                  <input
                    type="number"
                    value={formData.duration_weeks ?? ''}
                    onChange={(e) => setFormData({ ...formData, duration_weeks: parseInt(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-slate-50 font-bold text-indigo-700"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Certificate Received</label>
                  <select
                    value={formData.certificate_received || 'No'}
                    onChange={(e) => setFormData({ ...formData, certificate_received: e.target.value })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white"
                  >
                    <option value="Yes">Yes</option>
                    <option value="No">No</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Internship Offered By</label>
                  <input
                    type="text"
                    value={formData.offered_by || formData.internship_offered_by || ''}
                    onChange={(e) => setFormData({ ...formData, offered_by: e.target.value, internship_offered_by: e.target.value })}
                    placeholder="e.g. On-Campus Drive, AICTE"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Track (Regular/AEP/IDEA LAB)</label>
                  <input
                    type="text"
                    value={formData.regular_internship || 'Regular'}
                    onChange={(e) => setFormData({ ...formData, regular_internship: e.target.value })}
                    placeholder="e.g. Regular, AEP, IDEA LAB"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
                <div className="sm:col-span-2">
                  <label className="block font-semibold text-slate-700 uppercase mb-1">Organization Address</label>
                  <input
                    type="text"
                    value={formData.organization_address || ''}
                    onChange={(e) => setFormData({ ...formData, organization_address: e.target.value })}
                    placeholder="Full corporate postal address"
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-200 flex justify-end space-x-3">
                <TactileButton
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </TactileButton>
                <TactileButton
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={saving}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs"
                >
                  {saving ? 'Saving...' : 'Save Internship Record'}
                </TactileButton>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* 3. CERTIFICATE UPLOAD MODAL */}
      {certModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
            <div className="flex justify-between items-center pb-2 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-indigo-600" />
                <h3 className="text-base font-bold text-slate-900">Upload Internship Certificate</h3>
              </div>
              <button onClick={() => setCertModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleUploadCertSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-semibold mb-1">
                  Select Certificate Document (PDF / JPG / PNG, Max 25MB)
                </label>
                <input
                  type="file"
                  required
                  accept="application/pdf,image/jpeg,image/png"
                  onChange={(e) => setCertFile(e.target.files ? e.target.files[0] : null)}
                  className="w-full p-2 border border-slate-300 rounded-lg text-xs"
                />
              </div>

              <div className="pt-2 flex justify-end space-x-2">
                <TactileButton
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setCertModalOpen(false)}
                  className="rounded-xl text-xs"
                >
                  Cancel
                </TactileButton>
                <TactileButton
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={uploadingCert || !certFile}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs"
                >
                  {uploadingCert ? 'Uploading...' : 'Upload Certificate'}
                </TactileButton>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
