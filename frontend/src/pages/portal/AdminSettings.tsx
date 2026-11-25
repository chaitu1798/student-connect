import React from 'react';
import { Settings, ShieldCheck, Database, HardDrive, Cpu, CheckCircle, Server, Lock } from 'lucide-react';
import { AssetoCard } from '../../components/ui/AssetoCard';

export const AdminSettings: React.FC = () => {
  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
        <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
          <Settings className="w-4 h-4" />
          <span>System Parameters & Environment</span>
          <span>•</span>
          <span className="text-[#64748B] font-normal">Active Configuration</span>
        </div>
        <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
          Application Settings & Governance Diagnostics
        </h1>
        <p className="text-xs text-[#64748B] mt-1">
          Database connection parameters, cryptographic security standards, and institutional compliance thresholds.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database Architecture */}
        <AssetoCard
          title="Database & Storage Architecture"
          subtitle="Enterprise persistence layer with transactional guarantees"
        >
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">ORM Framework:</span>
              <span className="font-mono font-bold text-[#16283B]">SQLAlchemy 2.0 (Alembic Ready)</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Transactions:</span>
              <span className="asseto-badge-emerald">ACID Compliant with Rollback Safety</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Identifier Scheme:</span>
              <span className="font-mono text-[#16283B]">UUID Primary Keys + Roll No Indexed</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Soft Deletion:</span>
              <span className="asseto-badge-blue">Enabled (is_archived & is_deleted)</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-[#64748B]">Schema Tables:</span>
              <span className="font-semibold text-[#16283B]">26 Normalized Tables</span>
            </div>
          </div>
        </AssetoCard>

        {/* Security Parameters */}
        <AssetoCard
          title="Security & Institutional Compliance"
          subtitle="Cryptographic protection standards and privacy filters"
        >
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Authentication Scheme:</span>
              <span className="font-mono text-[#16283B]">JWT Bearer Tokens (HS256)</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Credential Encryption:</span>
              <span className="font-mono text-[#16283B]">Passlib Bcrypt with Salt</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">PII Protection:</span>
              <span className="asseto-badge-emerald">Aadhaar & PAN Masked in Public APIs</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b border-[#F1F4F7]">
              <span className="text-[#64748B]">Document Access:</span>
              <span className="asseto-badge-blue">Object-Level Authorized (No Public S3)</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-[#64748B]">Audit Logging:</span>
              <span className="font-semibold text-emerald-700">100% Actions Tracked to AuditLog</span>
            </div>
          </div>
        </AssetoCard>
      </div>
    </div>
  );
};
