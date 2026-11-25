import React, { useState, useEffect } from 'react';
import { ShieldCheck, Check, X, Search, Lock } from 'lucide-react';
import { apiClient } from '../../api/client';
import { PublicPermission } from '../../types';

export const AdminPublicPermissions: React.FC = () => {
  const [perms, setPerms] = useState<PublicPermission[]>([]);
  const [search, setSearch] = useState('');
  const [savingRoll, setSavingRoll] = useState<string | null>(null);

  const fetchPermissions = () => {
    apiClient.get('/admin/permissions')
      .then((res) => setPerms(res.data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchPermissions();
  }, []);

  const handleToggle = async (perm: PublicPermission, field: 'is_public_approved' | 'publish_gender' | 'publish_cgpa' | 'publish_internships') => {
    setSavingRoll(perm.roll_no);
    const updated = {
      is_public_approved: field === 'is_public_approved' ? !perm.is_public_approved : perm.is_public_approved,
      publish_gender: field === 'publish_gender' ? !perm.publish_gender : perm.publish_gender,
      publish_cgpa: field === 'publish_cgpa' ? !perm.publish_cgpa : perm.publish_cgpa,
      publish_internships: field === 'publish_internships' ? !perm.publish_internships : perm.publish_internships,
      student_consent_given: perm.student_consent_given,
    };

    try {
      await apiClient.put(`/admin/permissions/${perm.roll_no}`, updated);
      fetchPermissions();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update public permissions.');
    } finally {
      setSavingRoll(null);
    }
  };

  const filtered = perms.filter(
    (p) =>
      p.roll_no.toLowerCase().includes(search.toLowerCase()) ||
      p.student_name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold font-serif text-slate-900">Public Profile Approval & Privacy Settings</h1>
          <p className="text-xs text-slate-500 mt-1">
            Student consent & administrator approval are strictly required before any profile is visible in public directories.
          </p>
        </div>
        <div className="relative max-w-xs w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search student or roll no..."
            className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-xs"
          />
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-[11px] font-semibold text-slate-700 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3.5">Roll No</th>
                <th className="px-5 py-3.5">Student Name</th>
                <th className="px-5 py-3.5">Branch</th>
                <th className="px-5 py-3.5 text-center">Public Approved</th>
                <th className="px-5 py-3.5 text-center">Publish Gender</th>
                <th className="px-5 py-3.5 text-center">Publish CGPA</th>
                <th className="px-5 py-3.5 text-center">Publish Internships</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {filtered.map((p) => (
                <tr key={p.roll_no} className="hover:bg-slate-50">
                  <td className="px-5 py-3.5 font-mono font-bold text-blue-700">{p.roll_no}</td>
                  <td className="px-5 py-3.5 font-medium text-slate-900">{p.student_name}</td>
                  <td className="px-5 py-3.5">{p.branch || '-'}</td>
                  
                  {/* Public Approved Toggle */}
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => handleToggle(p, 'is_public_approved')}
                      disabled={savingRoll === p.roll_no}
                      className={`px-3 py-1 rounded-full text-[11px] font-bold transition ${
                        p.is_public_approved 
                          ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' 
                          : 'bg-slate-100 text-slate-600 border border-slate-200'
                      }`}
                    >
                      {p.is_public_approved ? 'APPROVED' : 'PRIVATE'}
                    </button>
                  </td>

                  {/* Gender Toggle */}
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => handleToggle(p, 'publish_gender')}
                      disabled={savingRoll === p.roll_no}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        p.publish_gender ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-400'
                      }`}
                    >
                      {p.publish_gender ? 'Visible' : 'Hidden'}
                    </button>
                  </td>

                  {/* CGPA Toggle */}
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => handleToggle(p, 'publish_cgpa')}
                      disabled={savingRoll === p.roll_no}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        p.publish_cgpa ? 'bg-blue-100 text-blue-800' : 'bg-slate-100 text-slate-400'
                      }`}
                    >
                      {p.publish_cgpa ? 'Visible' : 'Hidden'}
                    </button>
                  </td>

                  {/* Internships Toggle */}
                  <td className="px-5 py-3.5 text-center">
                    <button
                      onClick={() => handleToggle(p, 'publish_internships')}
                      disabled={savingRoll === p.roll_no}
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold ${
                        p.publish_internships ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-100 text-slate-400'
                      }`}
                    >
                      {p.publish_internships ? 'Visible' : 'Hidden'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
