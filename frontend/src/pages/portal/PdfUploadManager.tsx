import React, { useState } from 'react';
import { FileText, Upload, CheckCircle2, AlertTriangle, ArrowRight, Save, RefreshCw } from 'lucide-react';
import { apiClient } from '../../api/client';

export const PdfUploadManager: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [extractResult, setExtractResult] = useState<any | null>(null);
  const [reviewedData, setReviewedData] = useState<any>({});
  const [committing, setCommitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setExtractResult(null);
      setSuccessMessage('');
    }
  };

  const handleExtract = async () => {
    if (!file) return;
    setExtracting(true);
    setExtractResult(null);
    setSuccessMessage('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await apiClient.post('/pdf/extract', formData);
      setExtractResult(res.data);
      setReviewedData(res.data.extracted_data || {});
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to extract text from PDF.');
    } finally {
      setExtracting(false);
    }
  };

  const handleCommit = async () => {
    if (!extractResult || !reviewedData.roll_no) {
      alert('Roll Number is mandatory to save student details.');
      return;
    }

    setCommitting(true);
    try {
      const res = await apiClient.post(`/pdf/commit/${extractResult.history_id}`, reviewedData);
      setSuccessMessage(res.data.message || 'Record saved successfully.');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to save record.');
    } finally {
      setCommitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
        <h1 className="text-xl sm:text-2xl font-bold text-[#16283B]">PDF Upload & Text Extraction</h1>
        <p className="text-xs text-[#64748B] mt-1">
          Upload student application PDFs, marks memos, or certificates. Employs text parsing and OCR fallback to extract student credentials with human review.
        </p>
      </div>

      {/* Upload Box */}
      <div className="bg-white p-6 sm:p-8 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] space-y-4">
        <div className="border-2 border-dashed border-[#E8ECEF] hover:border-[#1758A2] rounded-2xl p-6 text-center space-y-3 transition">
          <FileText className="w-8 h-8 text-[#94A3B8] mx-auto" />
          <div>
            <label className="cursor-pointer text-sm font-semibold text-[#1758A2] hover:underline">
              Choose a PDF document
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
            <p className="text-xs text-[#64748B] mt-1">Accepts native and scanned PDF files (up to 10MB)</p>
          </div>
          {file && (
            <div className="inline-flex items-center space-x-2 bg-[#F6F6F6] text-[#16283B] px-3 py-1.5 rounded-xl text-xs font-mono font-medium border border-[#E8ECEF]">
              <span>{file.name}</span>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleExtract}
            disabled={!file || extracting}
            className="asseto-btn-primary text-xs py-2 px-5 rounded-xl disabled:opacity-50"
          >
            {extracting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            <span>{extracting ? 'Extracting Text & OCR...' : 'Upload & Extract Details'}</span>
          </button>
        </div>
      </div>

      {/* Extraction Review and Manual Correction */}
      {extractResult && (
        <div className="bg-white p-6 sm:p-8 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] space-y-6">
          <div className="pb-4 border-b border-[#F1F4F7]">
            <h2 className="text-base font-bold text-[#16283B]">
              Review & Correct Extracted Information
            </h2>
            <p className="text-xs text-[#64748B] mt-0.5">
              Review and verify fields before committing changes transactionally to the database.
            </p>
          </div>

          {extractResult.matched_existing_student && (
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800">
              <strong>Existing Student Found in Database:</strong>
              <div className="mt-1 font-mono">
                Roll No: {extractResult.matched_existing_student.roll_no} | Name: {extractResult.matched_existing_student.full_name} | Branch: {extractResult.matched_existing_student.branch}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Extracted Roll No *
              </label>
              <input
                type="text"
                value={reviewedData.roll_no || ''}
                onChange={(e) => setReviewedData({ ...reviewedData, roll_no: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm font-mono font-bold"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Extracted Full Name
              </label>
              <input
                type="text"
                value={reviewedData.full_name || ''}
                onChange={(e) => setReviewedData({ ...reviewedData, full_name: e.target.value.toUpperCase() })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm uppercase"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Branch</label>
              <input
                type="text"
                value={reviewedData.branch || ''}
                onChange={(e) => setReviewedData({ ...reviewedData, branch: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">CGPA</label>
              <input
                type="number"
                step="0.01"
                value={reviewedData.cgpa ?? ''}
                onChange={(e) => setReviewedData({ ...reviewedData, cgpa: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Contact No</label>
              <input
                type="text"
                value={reviewedData.contact_no || ''}
                onChange={(e) => setReviewedData({ ...reviewedData, contact_no: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Email</label>
              <input
                type="email"
                value={reviewedData.email || ''}
                onChange={(e) => setReviewedData({ ...reviewedData, email: e.target.value })}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm"
              />
            </div>
          </div>

          {/* Raw Text Snippet */}
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase mb-1">Raw Extracted Text Snippet</label>
            <textarea
              readOnly
              rows={3}
              value={extractResult.raw_text || ''}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-xs font-mono text-slate-600"
            />
          </div>

          {successMessage && (
            <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs rounded-lg flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{successMessage}</span>
            </div>
          )}

          <div className="flex justify-end space-x-3">
            <button
              onClick={handleCommit}
              disabled={committing || !reviewedData.roll_no}
              className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl text-sm font-semibold shadow transition flex items-center space-x-2 cursor-pointer"
            >
              <Save className="w-4 h-4" />
              <span>{committing ? 'Saving Record...' : 'Confirm & Save to Database'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
