import React from 'react';
import { Award, ShieldCheck, CheckCircle2, MapPin, Mail, Phone, Clock } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="bg-white min-h-[75vh]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-20 space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-[#6E6E73]">
            Placement & Internship Cell
          </p>
          <h1 className="text-4xl sm:text-5xl font-semibold tracking-[-0.03em] text-[#1D1D1F] leading-tight">
            Excellence in engineering and industry connect.
          </h1>
          <p className="text-base sm:text-lg text-[#6E6E73] leading-relaxed">
            Vignan's Institute Of Information Technology maintains a centralized digital repository of undergraduate students,
            academic records, standardized test qualifications, and accredited corporate internships.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
          <div className="p-8 bg-[#F5F5F7] rounded-3xl space-y-3">
            <ShieldCheck className="w-7 h-7 text-[#0071E3]" />
            <h3 className="text-base font-semibold text-[#1D1D1F]">100% Verified Profiles</h3>
            <p className="text-xs text-[#6E6E73] leading-relaxed">
              Every student profile is audited against official semester transcripts and university certificates.
            </p>
          </div>
          <div className="p-8 bg-[#F5F5F7] rounded-3xl space-y-3">
            <Award className="w-7 h-7 text-[#0071E3]" />
            <h3 className="text-base font-semibold text-[#1D1D1F]">Industry Partnerships</h3>
            <p className="text-xs text-[#6E6E73] leading-relaxed">
              Direct collaborations with top technology enterprises, research labs, and public sector undertakings.
            </p>
          </div>
          <div className="p-8 bg-[#F5F5F7] rounded-3xl space-y-3">
            <CheckCircle2 className="w-7 h-7 text-[#0071E3]" />
            <h3 className="text-base font-semibold text-[#1D1D1F]">ISO 9001:2015 Compliant</h3>
            <p className="text-xs text-[#6E6E73] leading-relaxed">
              Strict adherence to data privacy, AES-256-GCM encryption, and institutional audit standards.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export const ContactPage: React.FC = () => {
  return (
    <div className="bg-white min-h-[75vh]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-20 space-y-10">
        <div className="max-w-2xl space-y-3">
          <h1 className="text-4xl sm:text-5xl font-semibold tracking-[-0.03em] text-[#1D1D1F]">
            Contact Placement Cell
          </h1>
          <p className="text-base text-[#6E6E73]">
            Questions regarding student credential verification, recruitment drives, or corporate internship partnerships.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-[#F5F5F7] p-8 rounded-3xl space-y-5 text-sm">
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-[#0071E3] mt-0.5 shrink-0" />
              <div>
                <div className="font-semibold text-[#1D1D1F]">Campus Address</div>
                <p className="text-xs text-[#6E6E73] mt-1">
                  Office of Career Planning & Placements, Vignan's Institute Of Information Technology
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Phone className="w-5 h-5 text-[#0071E3] shrink-0" />
              <div>
                <div className="font-semibold text-[#1D1D1F]">Helpline</div>
                <p className="text-xs text-[#6E6E73]">+91 (040) 2345-6789 / 2345-6790</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Mail className="w-5 h-5 text-[#0071E3] shrink-0" />
              <div>
                <div className="font-semibold text-[#1D1D1F]">Official Email</div>
                <p className="text-xs text-[#6E6E73]">placements@institution.edu</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-[#0071E3] shrink-0" />
              <div>
                <div className="font-semibold text-[#1D1D1F]">Office Hours</div>
                <p className="text-xs text-[#6E6E73]">Monday – Friday: 9:00 AM – 5:00 PM IST</p>
              </div>
            </div>
          </div>

          <div className="bg-[#000000] text-white p-8 rounded-3xl flex flex-col justify-between space-y-6">
            <div className="space-y-2">
              <h3 className="text-xl font-semibold tracking-tight">Recruiter Verification</h3>
              <p className="text-sm text-[#A1A1A6] leading-relaxed">
                Recruiters seeking campus placement schedules or bulk student credential verification can contact the Placement Director directly.
              </p>
            </div>
            <div className="text-xs font-mono text-[#0071E3] bg-white/10 px-4 py-3 rounded-2xl">
              director.placements@institution.edu
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
