import React from 'react';
import { GraduationCap } from 'lucide-react';

export const Footer: React.FC<{ setCurrentView: (v: string) => void }> = ({ setCurrentView }) => {
  return (
    <footer className="bg-[#F5F5F7] text-[#6E6E73] border-t border-black/[0.08]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 pb-10 border-b border-black/[0.08]">
          {/* Col 1: Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[#1D1D1F]">
              <div className="w-7 h-7 rounded-full bg-[#1D1D1F] flex items-center justify-center text-white">
                <GraduationCap className="w-3.5 h-3.5" />
              </div>
              <span className="font-semibold text-xs tracking-tight">
                Vignan's Institute Of Information Technology
              </span>
            </div>
            <p className="text-xs leading-relaxed">
              Centralized academic repository for student credentials, verified internships, and placement records.
            </p>
          </div>

          {/* Col 2: Navigation */}
          <div>
            <h3 className="text-xs font-semibold text-[#1D1D1F] mb-3">Directory</h3>
            <ul className="space-y-2 text-xs">
              <li>
                <button onClick={() => setCurrentView('home')} className="hover:text-[#1D1D1F] transition cursor-pointer">
                  Overview
                </button>
              </li>
              <li>
                <button onClick={() => setCurrentView('student-directory')} className="hover:text-[#1D1D1F] transition cursor-pointer">
                  Student Directory
                </button>
              </li>
              <li>
                <button onClick={() => setCurrentView('internship-directory')} className="hover:text-[#1D1D1F] transition cursor-pointer">
                  Internship Records
                </button>
              </li>
            </ul>
          </div>

          {/* Col 3: Institution */}
          <div>
            <h3 className="text-xs font-semibold text-[#1D1D1F] mb-3">Institution</h3>
            <ul className="space-y-2 text-xs">
              <li>
                <button onClick={() => setCurrentView('about')} className="hover:text-[#1D1D1F] transition cursor-pointer">
                  About Placement Cell
                </button>
              </li>
              <li>
                <button onClick={() => setCurrentView('contact')} className="hover:text-[#1D1D1F] transition cursor-pointer">
                  Contact & Verification
                </button>
              </li>
              <li>
                <button onClick={() => setCurrentView('admin-login')} className="hover:text-[#0071E3] transition cursor-pointer">
                  Administrator Portal
                </button>
              </li>
            </ul>
          </div>

          {/* Col 4: Privacy */}
          <div>
            <h3 className="text-xs font-semibold text-[#1D1D1F] mb-3">Data Privacy</h3>
            <p className="text-xs leading-relaxed">
              Government IDs, personal contact details, and private records are encrypted and never publicly exposed.
            </p>
          </div>
        </div>

        <div className="pt-6 text-[11px] flex flex-col sm:flex-row justify-between items-center gap-3">
          <div>
            Copyright © {new Date().getFullYear()} Vignan's Institute Of Information Technology. All rights reserved.
          </div>
          <div className="flex gap-5">
            <span>Privacy Policy</span>
            <span>ISO 9001:2015</span>
            <span>Verified Records</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
