import React, { useState, useEffect } from 'react';
import { Activity, Search, Clock, ShieldCheck, Filter } from 'lucide-react';
import { apiClient } from '../../api/client';
import { AssetoCard } from '../../components/ui/AssetoCard';

export const AdminAuditLogs: React.FC = () => {
  const [logs, setLogs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [actionFilter, setActionFilter] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchLogs = () => {
    setLoading(true);
    let url = `/admin/audit-logs?page=1&page_size=50`;
    if (actionFilter) url += `&action=${encodeURIComponent(actionFilter)}`;

    apiClient.get(url)
      .then((res) => {
        setLogs(res.data.items || []);
        setTotal(res.data.total || 0);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter]);

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
            <Activity className="w-4 h-4" />
            <span>Immutable Security Logs</span>
            <span>•</span>
            <span className="text-[#64748B] font-normal">{total} Audit Events Logged</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
            System Activity & Governance Audit Trail
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Tamper-evident record of user authentication, student modifications, staged imports, and administrative approvals.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="py-2 px-3 text-xs bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl outline-none text-[#16283B]"
          >
            <option value="">All Action Types</option>
            <option value="LOGIN">LOGIN</option>
            <option value="CREATE">CREATE</option>
            <option value="UPDATE">UPDATE</option>
            <option value="DELETE">DELETE</option>
            <option value="IMPORT">IMPORT</option>
            <option value="EXPORT">EXPORT</option>
            <option value="APPROVE">APPROVE</option>
            <option value="REJECT">REJECT</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <AssetoCard noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#F8FAFC] text-[11px] font-semibold text-[#64748B] uppercase tracking-wider border-b border-[#E8ECEF]">
              <tr>
                <th className="px-5 py-3.5">Timestamp</th>
                <th className="px-5 py-3.5">User</th>
                <th className="px-5 py-3.5">Action</th>
                <th className="px-5 py-3.5">Entity Type</th>
                <th className="px-5 py-3.5">Target Identifier</th>
                <th className="px-5 py-3.5">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F4F7]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-[#64748B]">
                    <div className="w-8 h-8 border-2 border-[#1758A2] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <span>Loading audit records...</span>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-12 text-center text-[#64748B]">
                    No audit records matching criteria.
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[#F8FAFC] transition">
                    <td className="px-5 py-3 text-[#64748B] font-mono text-[11px] whitespace-nowrap">
                      {log.created_at ? new Date(log.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="px-5 py-3 font-semibold text-[#16283B]">
                      {log.username || 'System'}
                    </td>
                    <td className="px-5 py-3">
                      <span className="asseto-badge-blue text-[10px]">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[#64748B] uppercase font-mono text-[11px]">
                      {log.entity_type}
                    </td>
                    <td className="px-5 py-3 font-mono font-semibold text-[#1758A2]">
                      {log.entity_id}
                    </td>
                    <td className="px-5 py-3 text-[#16283B] max-w-md truncate">
                      {log.details || '—'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </AssetoCard>
    </div>
  );
};
