import React, { useState, useEffect } from 'react';
import {
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertTriangle,
  Download,
  RefreshCw,
  Clock,
  Send,
  Eye,
  Info,
  Layers,
  ArrowRight
} from 'lucide-react';
import { apiClient } from '../../api/client';

export const ExcelImportManager: React.FC = () => {
  const [templateType, setTemplateType] = useState<'student' | 'internship'>('student');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [activeJob, setActiveJob] = useState<any | null>(null);
  const [previewData, setPreviewData] = useState<any | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [history, setHistory] = useState<any[]>([]);
  const [selectedRow, setSelectedRow] = useState<any | null>(null);

  const fetchHistory = () => {
    apiClient.get('/client/imports')
      .then((res) => setHistory(res.data))
      .catch((err) => console.error('Error fetching import jobs:', err));
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setActiveJob(null);
      setPreviewData(null);
    }
  };

  const handleUploadAndStage = async () => {
    if (!file) return;
    setUploading(true);
    setActiveJob(null);
    setPreviewData(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('template_type', templateType);

    try {
      const res = await apiClient.post('/client/imports', formData);
      const job = res.data;
      setActiveJob(job);
      fetchHistory();
      // Fetch full preview
      await loadPreview(job.id);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to process document upload.');
    } finally {
      setUploading(false);
    }
  };

  const loadPreview = async (jobId: string) => {
    setPreviewLoading(true);
    try {
      const res = await apiClient.get(`/client/imports/${jobId}/preview`);
      setPreviewData(res.data);
      setActiveJob(res.data.job);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to fetch staged job preview.');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSubmitForApproval = async () => {
    if (!activeJob) return;
    if (!window.confirm('Are you sure you want to submit this staged import for Administrator approval? Once submitted, an administrator will review all changes.')) {
      return;
    }

    setSubmitting(true);
    try {
      await apiClient.post(`/client/imports/${activeJob.id}/submit`);
      alert('Staged import submitted successfully! An administrator will review and approve these changes.');
      fetchHistory();
      // Reload preview to see updated status
      await loadPreview(activeJob.id);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit import job.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-[#16283B]">Document Upload & Staged Import Engine</h1>
          <p className="text-xs text-[#64748B] mt-1">
            Zero-direct-overwrite staging. Spreadsheets and documents are staged, validated, and diff-analyzed before administrator approval.
          </p>
        </div>

        {/* Template Downloads */}
        <div className="flex flex-wrap gap-2 text-xs">
          <a
            href="/templates/student_template.xlsx"
            download
            className="asseto-btn-secondary text-xs py-2 px-3 rounded-xl"
          >
            <Download className="w-3.5 h-3.5 text-[#1758A2]" />
            <span>Student Template (.xlsx)</span>
          </a>
          <a
            href="/templates/internship_template.xlsx"
            download
            className="asseto-btn-secondary text-xs py-2 px-3 rounded-xl"
          >
            <Download className="w-3.5 h-3.5 text-[#1758A2]" />
            <span>Internship Template (.xlsx)</span>
          </a>
        </div>
      </div>

      {/* Step 1: Select Template & File */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] space-y-6">
        <h2 className="text-sm font-bold text-[#16283B] uppercase tracking-wider">
          1. Select Schema & Document File
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div
            onClick={() => { setTemplateType('student'); setActiveJob(null); setPreviewData(null); }}
            className={`p-4 rounded-xl border-2 transition cursor-pointer flex items-center space-x-3 ${templateType === 'student' ? 'border-[#1758A2] bg-[#1758A2]/5' : 'border-[#E8ECEF] hover:border-slate-300'
              }`}
          >
            <FileSpreadsheet className={`w-6 h-6 ${templateType === 'student' ? 'text-[#1758A2]' : 'text-[#64748B]'}`} />
            <div>
              <div className="text-sm font-bold text-[#16283B]">Student Information Schema</div>
              <div className="text-xs text-[#64748B]">41 academic, personal, CRT, SSC, Inter & ID fields</div>
            </div>
          </div>

          <div
            onClick={() => { setTemplateType('internship'); setActiveJob(null); setPreviewData(null); }}
            className={`p-4 rounded-xl border-2 transition cursor-pointer flex items-center space-x-3 ${templateType === 'internship' ? 'border-[#1758A2] bg-[#1758A2]/5' : 'border-[#E8ECEF] hover:border-slate-300'
              }`}
          >
            <FileSpreadsheet className={`w-6 h-6 ${templateType === 'internship' ? 'text-[#1758A2]' : 'text-[#64748B]'}`} />
            <div>
              <div className="text-sm font-bold text-[#16283B]">Internship Information Schema</div>
              <div className="text-xs text-[#64748B]">22 organization, role, stipend, duration & certificate fields</div>
            </div>
          </div>
        </div>

        {/* File Picker */}
        <div className="border-2 border-dashed border-[#E8ECEF] hover:border-[#1758A2] rounded-2xl p-6 text-center space-y-3 transition">
          <Upload className="w-8 h-8 text-[#94A3B8] mx-auto" />
          <div>
            <label className="cursor-pointer text-sm font-semibold text-[#1758A2] hover:underline">
              Choose an Excel, CSV, or PDF document
              <input
                type="file"
                accept=".xlsx, .xls, .csv, .pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
            <p className="text-xs text-[#64748B] mt-1">Supports .xlsx, .xls, .csv, and scanned/digital .pdf documents</p>
          </div>
          {file && (
            <div className="inline-flex items-center space-x-2 bg-[#F6F6F6] text-[#16283B] px-3 py-1.5 rounded-xl text-xs font-mono font-medium border border-[#E8ECEF]">
              <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleUploadAndStage}
            disabled={!file || uploading}
            className="asseto-btn-primary text-xs py-2.5 px-5 rounded-xl disabled:opacity-50"
          >
            {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Layers className="w-4 h-4" />}
            <span>{uploading ? 'Extracting & Staging...' : 'Upload & Generate Staged Preview'}</span>
          </button>
        </div>
      </div>

      {/* Step 2: Staged Diff Preview & Review */}
      {previewLoading && (
        <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center space-y-2">
          <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mx-auto" />
          <p className="text-sm text-slate-600 font-medium">Loading staged records and comparing against master database...</p>
        </div>
      )}

      {previewData && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-900 font-serif">
                  Staged Document Preview: {previewData.job.file_name}
                </h2>
                <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${previewData.job.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                    previewData.job.status === 'SUBMITTED' ? 'bg-amber-100 text-amber-800' :
                      previewData.job.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                        'bg-slate-100 text-slate-700'
                  }`}>
                  {previewData.job.status}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Template: <strong className="capitalize">{previewData.job.template_type}</strong> | Staged ID: <span className="font-mono">{previewData.job.id.slice(0, 8)}...</span>
              </p>
            </div>

            {/* Metrics Chips */}
            <div className="flex flex-wrap gap-2 text-xs">
              <span className="px-3 py-1 bg-slate-100 text-slate-800 rounded-lg font-medium">
                Total: <strong>{previewData.job.total_rows}</strong>
              </span>
              <span className="px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-lg font-medium">
                Valid: <strong>{previewData.job.valid_rows}</strong>
              </span>
              <span className="px-3 py-1 bg-blue-50 text-blue-800 border border-blue-200 rounded-lg font-medium">
                Changes Detected: <strong>{previewData.job.diff_rows}</strong>
              </span>
              {previewData.job.error_rows > 0 && (
                <span className="px-3 py-1 bg-red-50 text-red-800 border border-red-200 rounded-lg font-medium">
                  Errors: <strong>{previewData.job.error_rows}</strong>
                </span>
              )}
            </div>
          </div>

          {/* Staged Rows Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Extracted Records & Proposed Changes
            </h3>
            <div className="overflow-x-auto border border-slate-200 rounded-xl max-h-96">
              <table className="w-full text-left text-xs text-slate-600">
                <thead className="bg-slate-50 text-[11px] font-semibold text-slate-700 uppercase tracking-wider sticky top-0 border-b border-slate-200">
                  <tr>
                    <th className="px-4 py-3">Row #</th>
                    <th className="px-4 py-3">Roll Number</th>
                    <th className="px-4 py-3">Extracted Name</th>
                    <th className="px-4 py-3">Branch</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Proposed Diffs (Old ➔ New)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {previewData.rows.map((row: any) => {
                    const norm = row.normalized_data || {};
                    return (
                      <tr
                        key={row.id}
                        onClick={() => setSelectedRow(row)}
                        className={`hover:bg-blue-50/40 cursor-pointer ${selectedRow?.id === row.id ? 'bg-blue-50/60' : ''}`}
                      >
                        <td className="px-4 py-2.5 font-mono text-slate-500">{row.row_index}</td>
                        <td className="px-4 py-2.5 font-mono font-bold text-slate-900">{row.roll_number || '-'}</td>
                        <td className="px-4 py-2.5 text-slate-800">{norm.full_name || norm.student_name || '-'}</td>
                        <td className="px-4 py-2.5 text-slate-600">{norm.branch || '-'}</td>
                        <td className="px-4 py-2.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${row.status === 'VALID' ? 'bg-emerald-100 text-emerald-800' :
                              row.status === 'DIFF_DETECTED' ? 'bg-blue-100 text-blue-800' :
                                'bg-red-100 text-red-800'
                            }`}>
                            {row.status}
                          </span>
                        </td>
                        <td className="px-4 py-2.5">
                          {row.changes && row.changes.length > 0 ? (
                            <div className="flex flex-wrap gap-1.5">
                              {row.changes.map((c: any) => (
                                <span key={c.id} className="inline-flex items-center space-x-1 px-2 py-0.5 bg-amber-50 text-amber-900 border border-amber-200 rounded text-[10px] font-mono">
                                  <strong>{c.field_name}:</strong>
                                  <span className="line-through text-slate-400">{c.old_value || 'None'}</span>
                                  <span>➔</span>
                                  <span className="font-bold text-emerald-700">{c.new_value}</span>
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-slate-400 text-[11px]">No changes against master</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Submission Banner */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="text-xs text-slate-600 space-y-1">
              <div className="font-bold text-slate-900 flex items-center space-x-1.5">
                <Info className="w-4 h-4 text-blue-600" />
                <span>Governance & Approval Rule:</span>
              </div>
              <p>Clients cannot modify the master database directly. Once you review and submit, an authorized Administrator will inspect these diffs and approve or reject.</p>
            </div>

            {previewData.job.status === 'DRAFT' || previewData.job.status === 'REJECTED' ? (
              <button
                onClick={handleSubmitForApproval}
                disabled={submitting}
                className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow transition flex items-center space-x-2 cursor-pointer shrink-0"
              >
                {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>{submitting ? 'Submitting...' : 'Submit for Administrator Approval'}</span>
              </button>
            ) : (
              <span className="text-xs font-semibold px-4 py-2 bg-slate-200 text-slate-700 rounded-lg">
                Job is {previewData.job.status}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Import History Table */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-base font-bold text-slate-900 font-serif flex items-center space-x-2">
          <Clock className="w-4 h-4 text-slate-500" />
          <span>Upload & Staged Job History</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-[11px] font-semibold text-slate-700 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Created At</th>
                <th className="px-4 py-3">Document Name</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Total Rows</th>
                <th className="px-4 py-3">Diff Rows</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Remarks / Review</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {history.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-6 text-center text-slate-400">
                    No upload jobs recorded yet.
                  </td>
                </tr>
              ) : (
                history.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50">
                    <td className="px-4 py-2.5 text-slate-400">
                      {new Date(job.created_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5 font-medium text-slate-800">
                      {job.file_name}
                    </td>
                    <td className="px-4 py-2.5 capitalize">{job.template_type}</td>
                    <td className="px-4 py-2.5 font-bold text-slate-900">{job.total_rows}</td>
                    <td className="px-4 py-2.5 font-bold text-blue-700">{job.diff_rows}</td>
                    <td className="px-4 py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${job.status === 'APPROVED' ? 'bg-emerald-100 text-emerald-800' :
                          job.status === 'SUBMITTED' ? 'bg-amber-100 text-amber-800' :
                            job.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                              'bg-slate-100 text-slate-700'
                        }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-slate-500 max-w-xs truncate">
                      {job.remarks || (job.reviewed_at ? `Reviewed at ${new Date(job.reviewed_at).toLocaleDateString()}` : 'Pending review')}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <button
                        onClick={() => loadPreview(job.id)}
                        className="text-blue-600 hover:text-blue-800 inline-flex items-center space-x-1 font-semibold"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
