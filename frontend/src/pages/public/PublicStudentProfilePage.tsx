import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ShieldCheck,
  Briefcase,
  GraduationCap,
  MapPin,
  AlertCircle,
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { PublicStudentProfile } from '../../types';
import { StudentAvatar } from '../../components/ui/StudentAvatar';

interface PublicStudentProfilePageProps {
  rollNo: string;
  setCurrentView: (view: string) => void;
}

export const PublicStudentProfilePage: React.FC<PublicStudentProfilePageProps> = ({
  rollNo,
  setCurrentView,
}) => {
  const [profile, setProfile] = useState<PublicStudentProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiClient.get(`/public/profile/${encodeURIComponent(rollNo)}`)
      .then((res) => {
        setProfile(res.data);
        setError(null);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || 'This profile is private or does not exist.');
      })
      .finally(() => setLoading(false));
  }, [rollNo]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-24 text-center space-y-4">
        <div className="w-8 h-8 border-2 border-[#0071E3] border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-[#6E6E73] text-sm">Verifying student credentials...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="max-w-lg mx-auto px-4 py-24 text-center space-y-4">
        <div className="w-14 h-14 bg-[#F5F5F7] text-[#1D1D1F] rounded-full flex items-center justify-center mx-auto">
          <AlertCircle className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-semibold tracking-tight text-[#1D1D1F]">Profile Not Available</h2>
        <p className="text-sm text-[#6E6E73]">{error}</p>
        <button
          onClick={() => setCurrentView('student-directory')}
          className="inline-flex items-center gap-1.5 bg-[#0071E3] text-white text-xs font-medium py-2.5 px-5 rounded-full cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Directory</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-[75vh]">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-6">
        <button
          onClick={() => setCurrentView('student-directory')}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-[#0071E3] hover:underline cursor-pointer"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Student Directory</span>
        </button>

        {/* Dark Apple Hero Card */}
        <div className="bg-[#000000] text-white rounded-[32px] p-8 sm:p-10 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <StudentAvatar
              rollNo={profile.roll_no}
              name={profile.full_name}
              size="2xl"
            />
            <div className="text-center sm:text-left">
              <div className="inline-flex items-center gap-1.5 text-xs font-medium text-[#0071E3] mb-2">
                <ShieldCheck className="w-4 h-4" />
                <span>Verified Student Profile</span>
              </div>
              <h1 className="text-3xl sm:text-4xl font-semibold tracking-[-0.025em] text-white">
                {profile.full_name}
              </h1>
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-2.5 mt-2 text-xs text-[#A1A1A6]">
                <span className="font-mono bg-white/10 text-white px-2.5 py-0.5 rounded-full">
                  {profile.roll_no}
                </span>
                <span>·</span>
                <span>{profile.branch}</span>
              </div>
            </div>
          </div>

          <div className="bg-white/[0.08] border border-white/[0.1] px-6 py-4 rounded-2xl text-center shrink-0 self-stretch sm:self-center">
            <div className="text-3xl font-semibold text-white tabular-nums">{profile.internship_count}</div>
            <div className="text-[11px] text-[#A1A1A6] mt-0.5">Internships</div>
          </div>
        </div>

        {/* Academic Overview Bento */}
        <div className="bg-[#F5F5F7] rounded-[32px] p-8">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-[#6E6E73] mb-5 flex items-center gap-1.5">
            <GraduationCap className="w-4 h-4 text-[#1D1D1F]" />
            <span>Academic Overview</span>
          </h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl">
              <span className="text-[11px] text-[#6E6E73] block">Department</span>
              <span className="text-sm font-semibold text-[#1D1D1F] mt-1 block truncate">
                {profile.branch || 'Engineering'}
              </span>
            </div>
            <div className="bg-white p-5 rounded-2xl">
              <span className="text-[11px] text-[#6E6E73] block">Year of Passing</span>
              <span className="text-sm font-semibold text-[#1D1D1F] mt-1 block">
                {profile.ug_year_of_pass || 'Class of 2025'}
              </span>
            </div>
            {profile.gender && (
              <div className="bg-white p-5 rounded-2xl">
                <span className="text-[11px] text-[#6E6E73] block">Gender</span>
                <span className="text-sm font-semibold text-[#1D1D1F] mt-1 block">{profile.gender}</span>
              </div>
            )}
            {profile.ug_cgpa !== null && profile.ug_cgpa !== undefined && (
              <div className="bg-white p-5 rounded-2xl">
                <span className="text-[11px] text-[#6E6E73] block">UG / B.Tech CGPA</span>
                <span className="text-sm font-semibold text-[#0071E3] mt-1 block">{profile.ug_cgpa} / 10.0</span>
              </div>
            )}
          </div>
        </div>

        {/* Verified Internships */}
        <div className="bg-[#F5F5F7] rounded-[32px] p-8 space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-[#1D1D1F] flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-[#1D1D1F]" />
              <span>Approved Internships</span>
            </h2>
            <span className="text-xs font-medium text-[#6E6E73]">
              {profile.internships?.length || 0} Records
            </span>
          </div>

          {(!profile.internships || profile.internships.length === 0) ? (
            <div className="p-8 text-center text-[#6E6E73] bg-white rounded-2xl text-xs">
              No public internship records published yet for this student.
            </div>
          ) : (
            <div className="space-y-3">
              {profile.internships.map((int: any, idx: number) => (
                <div
                  key={idx}
                  className="p-5 rounded-2xl bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-2"
                >
                  <div>
                    <h3 className="font-semibold text-[#1D1D1F] text-sm">
                      {int.role || 'Intern'} · {int.name_of_organization}
                    </h3>
                    <p className="text-xs text-[#6E6E73] flex items-center gap-1.5 mt-1">
                      <MapPin className="w-3.5 h-3.5" />
                      <span>{int.organization_district || 'Corporate Location'}</span>
                      <span>·</span>
                      <span>{int.category || 'Technical'}</span>
                    </p>
                  </div>
                  <span className="text-[11px] font-medium text-[#0071E3] bg-[#0071E3]/10 px-3 py-1 rounded-full self-start sm:self-center">
                    Verified Placement
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
