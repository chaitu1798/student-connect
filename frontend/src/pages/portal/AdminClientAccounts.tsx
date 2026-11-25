import React, { useState, useEffect } from 'react';
import { UserPlus, UserCheck, UserX, KeyRound, AlertTriangle, CheckCircle2, X, Users, Shield } from 'lucide-react';
import { apiClient } from '../../api/client';
import { User } from '../../types';
import { AssetoCard } from '../../components/ui/AssetoCard';
import { StudentAvatar } from '../../components/ui/StudentAvatar';

export const AdminClientAccounts: React.FC = () => {
  const [clients, setClients] = useState<User[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [newClient, setNewClient] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const fetchClients = () => {
    apiClient.get('/admin/clients')
      .then((res) => setClients(res.data))
      .catch((err) => console.error(err));
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await apiClient.post('/admin/clients', newClient);
      setModalOpen(false);
      setNewClient({ username: '', email: '', full_name: '', password: '' });
      fetchClients();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create client user.');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleActive = async (client: User) => {
    try {
      await apiClient.put(`/admin/clients/${client.id}`, { is_active: !client.is_active });
      fetchClients();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update user status.');
    }
  };

  const handleResetPassword = async (clientId: number) => {
    if (!confirm('Reset password to temporary password?')) return;
    try {
      const res = await apiClient.post(`/admin/clients/${clientId}/reset-password`);
      alert(`Password reset successfully!\nTemporary Password: ${res.data.temporary_password}`);
      fetchClients();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to reset password.');
    }
  };

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-[#E8ECEF] shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
            <Users className="w-4 h-4" />
            <span>Role-Based Access Control</span>
            <span>•</span>
            <span className="text-[#64748B] font-normal">{clients.length} Client Users</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
            Client & Department Accounts Management
          </h1>
          <p className="text-xs text-[#64748B] mt-1">
            Provision departmental officer accounts, manage activation status, and issue credential resets.
          </p>
        </div>

        <button
          onClick={() => setModalOpen(true)}
          className="asseto-btn-primary text-xs py-2 px-4 rounded-xl"
        >
          <UserPlus className="w-4 h-4" />
          <span>Provision New Client</span>
        </button>
      </div>

      {/* Clients Table Card */}
      <AssetoCard noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead className="bg-[#F8FAFC] text-[11px] font-semibold text-[#64748B] uppercase tracking-wider border-b border-[#E8ECEF]">
              <tr>
                <th className="px-5 py-3.5">User Profile</th>
                <th className="px-5 py-3.5">Username</th>
                <th className="px-5 py-3.5">Role</th>
                <th className="px-5 py-3.5">Account Status</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F4F7]">
              {clients.map((client) => (
                <tr key={client.id} className="hover:bg-[#F8FAFC] transition">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-3">
                      <StudentAvatar name={client.full_name} size="sm" />
                      <div>
                        <div className="font-semibold text-[#16283B]">{client.full_name}</div>
                        <div className="text-[11px] text-[#64748B] font-mono">{client.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-5 py-4 font-mono font-medium text-[#16283B]">
                    {client.username}
                  </td>
                  <td className="px-5 py-4">
                    <span className="asseto-badge-blue text-[10px]">
                      {client.role.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                        client.is_active
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-rose-50 text-rose-700 border border-rose-200'
                      }`}
                    >
                      {client.is_active ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-right space-x-2">
                    <button
                      onClick={() => handleToggleActive(client)}
                      className="asseto-btn-secondary text-[11px] py-1 px-2.5 rounded-lg"
                      title={client.is_active ? 'Deactivate Account' : 'Activate Account'}
                    >
                      {client.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                    <button
                      onClick={() => handleResetPassword(client.id)}
                      className="asseto-btn-secondary text-[11px] py-1 px-2.5 rounded-lg text-amber-700"
                      title="Reset Password"
                    >
                      <KeyRound className="w-3.5 h-3.5" />
                      <span>Reset PWD</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AssetoCard>

      {/* Create Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white border border-[#E8ECEF] rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#16283B]">Provision Client Account</h3>
              <button onClick={() => setModalOpen(false)} className="p-1 text-[#64748B]">
                <X className="w-5 h-5" />
              </button>
            </div>

            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl">
                {error}
              </div>
            )}

            <form onSubmit={handleCreateClient} className="space-y-3 text-xs">
              <div>
                <label className="block text-[#16283B] font-semibold mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={newClient.full_name}
                  onChange={(e) => setNewClient({ ...newClient, full_name: e.target.value })}
                  className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none"
                />
              </div>

              <div>
                <label className="block text-[#16283B] font-semibold mb-1">Username</label>
                <input
                  type="text"
                  required
                  value={newClient.username}
                  onChange={(e) => setNewClient({ ...newClient, username: e.target.value })}
                  className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none"
                />
              </div>

              <div>
                <label className="block text-[#16283B] font-semibold mb-1">Email Address</label>
                <input
                  type="email"
                  required
                  value={newClient.email}
                  onChange={(e) => setNewClient({ ...newClient, email: e.target.value })}
                  className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none"
                />
              </div>

              <div>
                <label className="block text-[#16283B] font-semibold mb-1">Initial Password</label>
                <input
                  type="password"
                  required
                  value={newClient.password}
                  onChange={(e) => setNewClient({ ...newClient, password: e.target.value })}
                  className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="asseto-btn-secondary text-xs py-2 px-4 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="asseto-btn-primary text-xs py-2 px-5 rounded-xl"
                >
                  {saving ? 'Creating...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
