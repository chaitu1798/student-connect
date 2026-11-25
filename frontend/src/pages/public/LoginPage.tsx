import React, { useState } from 'react';
import { Lock, User as UserIcon, ShieldCheck, AlertCircle, ArrowLeft, KeyRound, Building } from 'lucide-react';
import { apiClient } from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { VantaBackground } from '../../components/motion/VantaBackground';
import { SpotlightCard } from '../../components/ui/SpotlightCard';
import { DecryptedText } from '../../components/ui/DecryptedText';
import { TactileButton } from '../../components/ui/TactileButton';

interface LoginPageProps {
  initialRole?: string;
  setCurrentView: (view: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ setCurrentView }) => {
  const { login } = useAuth();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('vignan123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post('/auth/login', {
        username,
        password,
      });
      const data = res.data;
      login(data.access_token, data.user);
      setCurrentView('admin-dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid username or password.');
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = () => {
    setUsername('admin');
    setPassword('vignan123');
    setError('');
  };

  return (
    <VantaBackground className="min-h-[90vh] flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-md my-8">
        <SpotlightCard
          className="rounded-2xl border border-slate-800/80 bg-slate-900/90 backdrop-blur-xl shadow-2xl text-slate-100 overflow-hidden"
          spotlightColor="rgba(56, 189, 248, 0.12)"
        >
          {/* Card Top Header */}
          <div className="p-6 sm:p-8 border-b border-slate-800/80 text-center relative">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#1758A2]/20 border border-[#1758A2]/40 text-[#6499CD] mb-3 shadow-inner">
              <ShieldCheck className="w-6 h-6" />
            </div>

            <div className="text-[11px] font-mono tracking-widest text-sky-400 uppercase mb-1">
              <DecryptedText text="Institutional Administration" speed={35} />
            </div>

            <h1 className="text-xl sm:text-2xl font-semibold text-white tracking-tight">
              Administrator Portal Login
            </h1>
            <p className="text-xs text-slate-400 mt-1.5 max-w-xs mx-auto leading-relaxed">
              Secure institutional academic ledger, internship repository, and verified student credentials.
            </p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="p-6 sm:p-8 space-y-4">
            {error && (
              <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-lg text-red-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
                <span className="leading-snug">{error}</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Administrator username
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  className="w-full px-3.5 py-2.5 bg-slate-950/70 border border-slate-700/80 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500/30 text-sm text-white placeholder-slate-500 font-mono"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-slate-300">
                  Password credential
                </label>
                <span className="text-[11px] text-slate-500 font-mono">Default: vignan123</span>
              </div>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full px-3.5 py-2.5 bg-slate-950/70 border border-slate-700/80 rounded-lg focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500/30 text-sm text-white placeholder-slate-500 font-mono"
                />
              </div>
            </div>

            <div className="pt-2">
              <TactileButton
                type="submit"
                loading={loading}
                variant="primary"
                size="md"
                className="w-full bg-[#1758A2] hover:bg-[#12427a] text-white font-semibold shadow-lg shadow-blue-500/10 focus:ring-blue-400"
              >
                {!loading && <Lock className="w-4 h-4 text-white" />}
                <span>{loading ? 'Verifying credentials...' : 'Authenticate & Enter Portal'}</span>
              </TactileButton>
            </div>

            {/* Quick Demo Fill Buttons for Reviewers */}
            <div className="pt-4 border-t border-slate-800/80">
              <button
                type="button"
                onClick={handleFillDemo}
                className="w-full py-2 px-3 bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800/80 rounded-lg text-slate-300 hover:text-white font-mono text-xs transition-colors flex items-center justify-between"
              >
                <span>admin / vignan123</span>
                <span className="text-[10px] text-sky-400 font-sans font-semibold">Auto-fill Default</span>
              </button>
            </div>
          </form>

          {/* Back to Public Site */}
          <div className="p-3.5 bg-slate-950/80 border-t border-slate-800/80 text-center">
            <button
              onClick={() => setCurrentView('home')}
              className="text-xs text-slate-400 hover:text-sky-400 font-medium inline-flex items-center gap-1.5 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to institutional home</span>
            </button>
          </div>
        </SpotlightCard>
      </div>
    </VantaBackground>
  );
};
