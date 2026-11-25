import React, { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  FileSpreadsheet, 
  Eye, 
  RefreshCw, 
  ShieldCheck, 
  ArrowRight,
  Filter,
  Check,
  X
} from 'lucide-react';
import { apiClient } from '../../api/client';

export const AdminImportApprovals: React.FC = () => {
  const [jobs, setJobs] = useState<any[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('SUBMITTED');
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [diffData, setDiffData] = useState<any | null>(null);
  const [diffLoading, setDiffLoading] = useState<boolean>(false);
  const [remarks, setRemarks] = useState<string>('');
  const [actionLoading, setActionLoading] = useState<boolean>(false);

  const fetchJobs = () => {
    setLoading(true);
    const url = statusFilter ? `/admin/imports?status_filter=${statusFilter}` : '/admin/imports';
    apiClient.get(url)
      .then((res) => setJobs(res.data))
      .catch((err) => console.error('Failed to fetch admin imports:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchJobs();
  }, [statusFilter]);

  const loadJobDiff = async (jobId: string) => {
    setSelectedJobId(jobId);
    setDiffLoading(true);
    setDiffData(null);
    setRemarks('');
    try {
      const res = await apiClient.get(`/admin/imports/${jobId}/diff`);
      setDiffData(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to fetch diff details.');
    } finally {
      setDiffLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedJobId) return;
    if (!window.confirm('Are you sure you want to approve this staged import? All proposed changes and new records will be transactionally applied to master tables.')) {
      return;
    }

    setActionLoading(true);
    try {
      const res = await apiClient.post(`/admin/imports/${selectedJobId}/approve`, { remarks });
      alert(res.data?.message || 'Staged changes successfully applied to master database!');
      setSelectedJobId(null);
      setDiffData(null);
      fetchJobs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to approve import job.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedJobId) return;
    if (!remarks.trim()) {
      alert('Please provide a reason or remarks for rejection so the client can correct the data.');
      return;
    }
    if (!window.confirm('Are you sure you want to reject this staged import?')) {
      return;
    }

    setActionLoading(true);
    try {
      const res = await apiClient.post(`/admin/imports/${selectedJobId}/reject`, { remarks });
      alert(res.data?.message || 'Import job rejected.');
      setSelectedJobId(null);
      setDiffData(null);
      fetchJobs();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reject import job.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col md:flex-row md:items-center justify-between gap-4 font-sans">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#16283B] flex items-center space-x-2">
            <ShieldCheck className="w-6 h-6 text-[#1758A2]" />
            <span>Administrator Import Approvals & Governance</span>
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Review proposed client staged uploads, inspect old-vs-new value diffs, and approve or reject transactional updates to master tables.
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center space-x-2 text-xs">
          <Filter className="w-4 h-4 text-[#64748B]" />
          <button
            onClick={() => setStatusFilter('SUBMITTED')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
              statusFilter === 'SUBMITTED' ? 'bg-[#1758A2] text-white shadow-xs' : 'bg-[#F6F6F6] text-[#64748B] hover:bg-[#F1F4F7]'
            }`}
          >
            Pending Review
          </button>
          <button
            onClick={() => setStatusFilter('')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
              statusFilter === '' ? 'bg-[#1758A2] text-white shadow-xs' : 'bg-[#F6F6F6] text-[#64748B] hover:bg-[#F1F4F7]'
            }`}
          >
            All Jobs
          </button>
          <button
            onClick={() => setStatusFilter('APPROVED')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
              statusFilter === 'APPROVED' ? 'bg-emerald-700 text-white shadow-xs' : 'bg-[#F6F6F6] text-[#64748B] hover:bg-[#F1F4F7]'
            }`}
          >
            Approved
          </button>
          <button
            onClick={() => setStatusFilter('REJECTED')}
            className={`px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer ${
              statusFilter === 'REJECTED' ? 'bg-rose-700 text-white shadow-xs' : 'bg-[#F6F6F6] text-[#64748B] hover:bg-[#F1F4F7]'
            }`}
          >
            Rejected
          </button>
        </div>
      </div>

      {/* Main Grid: Jobs List on Left / Diff Inspection on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Job Queue */}
        <div className={`${selectedJobId ? 'lg:col-span-5' : 'lg:col-span-12'} space-y-4`}>
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
                Staged Import Queue ({jobs.length})
              </h2>
              <button 
                onClick={fetchJobs} 
                className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>

            <div className="space-y-3">
              {jobs.length === 0 ? (
                <div className="p-8 text-center text-slate-400 text-xs">
                  No import jobs found with status filter: <strong>{statusFilter || 'ALL'}</strong>
                </div>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => loadJobDiff(job.id)}
                    className={`p-4 rounded-xl border transition cursor-pointer ${
                      selectedJobId === job.id 
                        ? 'border-blue-600 bg-blue-50/50 shadow-sm' 
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                          <FileSpreadsheet className="w-4 h-4 text-slate-500" />
                          <span>{job.file_name}</span>
                        </div>
                        <div className="text-xs text-slate-500 mt-1">
                          Template: <span className="capitalize font-semibold">{job.template_type}</span> | Total Rows: <strong>{job.total_rows}</strong>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                        job.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                        job.status === 'SUBMITTED' ? 'bg-amber-100 text-amber-800 animate-pulse' :
                        job.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                        'bg-slate-100 text-slate-700'
                      }`}>
                        {job.status}
                      </span>
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-3 pt-2 border-t border-slate-100">
                      <span>Created: {new Date(job.created_at).toLocaleDateString()}</span>
                      <span className="text-blue-600 font-semibold flex items-center space-x-1">
                        <span>Inspect Diffs ({job.diff_rows})</span>
                        <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Diff Inspector & Approval Actions */}
        {selectedJobId && (
          <div className="lg:col-span-7 space-y-6">
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <h2 className="text-lg font-bold font-serif text-slate-900">
                    Staged Changes Review
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5 font-mono">
                    Job ID: {selectedJobId}
                  </p>
                </div>
                <button
                  onClick={() => { setSelectedJobId(null); setDiffData(null); }}
                  className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {diffLoading && (
                <div className="p-8 text-center text-slate-500 space-y-2">
                  <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-600" />
                  <p className="text-xs">Computing diff comparison against master records...</p>
                </div>
              )}

              {diffData && (
                <div className="space-y-6">
                  {/* Summary Bar */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-center">
                      <span className="text-[10px] text-slate-400 font-semibold block uppercase">Status</span>
                      <span className="text-sm font-bold text-slate-800">{diffData.status}</span>
                    </div>
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-xl text-center">
                      <span className="text-[10px] text-blue-600 font-semibold block uppercase">Detected Diffs</span>
                      <span className="text-sm font-bold text-blue-700">{diffData.total_diff_changes} field changes</span>
                    </div>
                    <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-center">
                      <span className="text-[10px] text-slate-400 font-semibold block uppercase">Template</span>
                      <span className="text-sm font-bold text-slate-800 capitalize">{diffData.template_type}</span>
                    </div>
                  </div>

                  {/* Diffs Table */}
                  <div className="space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600">
                      Proposed Master Database Changes
                    </h3>

                    {diffData.changes.length === 0 ? (
                      <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl text-center text-slate-500 text-xs">
                        All rows in this file are identical to existing master records, or represent completely new inserts.
                      </div>
                    ) : (
                      <div className="overflow-x-auto border border-slate-200 rounded-xl max-h-80">
                        <table className="w-full text-left text-xs text-slate-600">
                          <thead className="bg-slate-50 text-[11px] font-semibold text-slate-700 uppercase tracking-wider sticky top-0 border-b border-slate-200">
                            <tr>
                              <th className="px-4 py-2.5">Roll No</th>
                              <th className="px-4 py-2.5">Entity / Scope</th>
                              <th className="px-4 py-2.5">Field</th>
                              <th className="px-4 py-2.5">Current Master Value</th>
                              <th className="px-4 py-2.5">Proposed Staged Value</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-200 font-mono text-[11px]">
                            {diffData.changes.map((c: any, idx: number) => (
                              <tr key={idx} className="hover:bg-slate-50">
                                <td className="px-4 py-2 font-bold text-slate-900">{c.roll_number}</td>
                                <td className="px-4 py-2 text-slate-500 capitalize">{c.entity_type}</td>
                                <td className="px-4 py-2 font-semibold text-blue-700">{c.field_name}</td>
                                <td className="px-4 py-2 text-red-600 line-through bg-red-50/50">
                                  {c.old_value !== null && c.old_value !== undefined ? String(c.old_value) : '<Empty>'}
                                </td>
                                <td className="px-4 py-2 text-emerald-700 font-bold bg-emerald-50/50">
                                  {c.new_value !== null && c.new_value !== undefined ? String(c.new_value) : '<Empty>'}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>

                  {/* Remarks Input */}
                  <div className="space-y-1.5">
                    <label className="text-xs font-bold text-slate-700">
                      Administrator Remarks / Reviewer Notes:
                    </label>
                    <textarea
                      value={remarks}
                      onChange={(e) => setRemarks(e.target.value)}
                      placeholder="Enter review comments or reason for rejection..."
                      rows={2}
                      className="w-full p-2.5 text-xs border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                    <div className="text-[11px] text-slate-400">
                      Approval commits changes atomically inside a database transaction.
                    </div>

                    <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
                      <button
                        onClick={handleReject}
                        disabled={actionLoading}
                        className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer disabled:opacity-50"
                      >
                        <XCircle className="w-4 h-4" />
                        <span>Reject Staged Import</span>
                      </button>

                      <button
                        onClick={handleApprove}
                        disabled={actionLoading}
                        className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow transition flex items-center space-x-1.5 cursor-pointer disabled:opacity-50"
                      >
                        {actionLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                        <span>Approve & Apply to Master</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
