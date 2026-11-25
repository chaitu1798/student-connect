import React, { useState } from 'react';
import { 
  BarChart3, 
  Download, 
  FileSpreadsheet, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { AssetoCard } from '../../components/ui/AssetoCard';

export const ReportsManager: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState('complete_student');
  const [downloading, setDownloading] = useState<'excel' | 'csv' | 'pdf' | null>(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const reportOptions = [
    { id: 'complete_student', name: 'Complete Student Master Report', desc: 'All registered students with academic, contact, personal, and category attributes.' },
    { id: 'academic', name: 'Student-Wise Academic Standings', desc: '10th, 12th/Diploma, and undergraduate CGPA standings and cohorts.' },
    { id: 'internship', name: 'Comprehensive Internship Report', desc: 'All corporate and research internships across disciplines and modes.' },
    { id: 'organization_wise', name: 'Organization-Wise Placement Report', desc: 'Recruiter and corporate engagement statistics and hired counts.' },
    { id: 'crt_registered', name: 'CRT Training Registration Report', desc: 'Students actively enrolled in Campus Recruitment Training.' },
    { id: 'backlog', name: 'Backlog Standing & Remedial Report', desc: 'Students with active standing backlogs requiring academic monitoring.' },
    { id: 'without_internships', name: 'Students Without Internships', desc: 'Students yet to fulfill mandatory industry internship credits.' },
    { id: 'certificate_pending', name: 'Internship Certificate Pending Report', desc: 'Internships lacking formal verified certificate documentation.' },
  ];

  const handleDownload = async (format: 'excel' | 'csv' | 'pdf') => {
    setDownloading(format);
    setErrorMsg('');
    setSuccessMsg('');

    const extMap: Record<string, string> = { excel: 'xlsx', csv: 'csv', pdf: 'pdf' };
    const mimeMap: Record<string, string> = {
      excel: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      csv: 'text/csv',
      pdf: 'application/pdf',
    };

    try {
      const res = await apiClient.get(`/reports/export?report_type=${selectedReport}&format=${format}`, {
        responseType: 'blob',
      });

      const blob = new Blob([res.data], { type: mimeMap[format] || 'application/octet-stream' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${selectedReport}_report.${extMap[format] || format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      const reportName = reportOptions.find((r) => r.id === selectedReport)?.name || selectedReport;
      setSuccessMsg(`Successfully generated and downloaded "${reportName}" in ${format.toUpperCase()} format.`);
    } catch (err: any) {
      console.error('Report export error:', err);
      setErrorMsg(err.response?.data?.detail || 'Failed to generate report export. Please check credentials.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Official Institutional Audit</span>
            <span>•</span>
            <span className="text-[#64748B] font-normal">Multi-Format Data Exports</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
            Institutional Reports & Analytics Exports
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Export production datasets in Excel (.xlsx), CSV, and PDF formats for academic governance, audits, and accreditation.
          </p>
        </div>
      </div>

      {/* Status Messages */}
      {successMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-2xl text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg('')} className="text-emerald-700 font-bold ml-2">✕</button>
        </div>
      )}

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-2xl text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg('')} className="text-rose-700 font-bold ml-2">✕</button>
        </div>
      )}

      {/* Report Types Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reportOptions.map((opt) => {
          const isSelected = selectedReport === opt.id;
          return (
            <div
              key={opt.id}
              onClick={() => {
                setSelectedReport(opt.id);
                setErrorMsg('');
                setSuccessMsg('');
              }}
              className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'border-[#1758A2] bg-[#1758A2]/5 shadow-sm'
                  : 'border-[#E8ECEF] bg-white hover:border-[#CBD5E1] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]'
              }`}
            >
              <div>
                <div className="flex justify-between items-start gap-2">
                  <h3 className="text-sm font-bold text-[#16283B]">{opt.name}</h3>
                  {isSelected && (
                    <CheckCircle2 className="w-4 h-4 text-[#1758A2] shrink-0" />
                  )}
                </div>
                <p className="text-xs text-[#64748B] mt-1.5 leading-relaxed">{opt.desc}</p>
              </div>

              {isSelected && (
                <div
                  className="mt-4 pt-3 border-t border-[#1758A2]/15 flex flex-wrap items-center gap-2"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() => handleDownload('excel')}
                    disabled={downloading !== null}
                    className="px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-xs flex items-center gap-1.5 transition"
                  >
                    <FileSpreadsheet className="w-3.5 h-3.5" />
                    <span>{downloading === 'excel' ? 'Exporting...' : 'Excel (.xlsx)'}</span>
                  </button>

                  <button
                    onClick={() => handleDownload('csv')}
                    disabled={downloading !== null}
                    className="px-3 py-1.5 bg-[#1758A2] hover:bg-[#124580] disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-xs flex items-center gap-1.5 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>{downloading === 'csv' ? 'Exporting...' : 'CSV (.csv)'}</span>
                  </button>

                  <button
                    onClick={() => handleDownload('pdf')}
                    disabled={downloading !== null}
                    className="px-3 py-1.5 bg-[#16283B] hover:bg-black disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-xs flex items-center gap-1.5 transition"
                  >
                    <FileText className="w-3.5 h-3.5" />
                    <span>{downloading === 'pdf' ? 'Rendering...' : 'PDF Document'}</span>
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
