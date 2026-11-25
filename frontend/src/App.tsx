import React, { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Navbar } from './components/layout/Navbar';
import { Footer } from './components/layout/Footer';
import { PortalLayout } from './components/layout/PortalLayout';
import { ChangePasswordModal } from './components/common/ChangePasswordModal';
import { useSmoothScroll } from './hooks/useSmoothScroll';

// Public Pages
import { HomePage } from './pages/public/HomePage';
import { StudentDirectoryPage } from './pages/public/StudentDirectoryPage';
import { PublicStudentProfilePage } from './pages/public/PublicStudentProfilePage';
import { InternshipDirectoryPage } from './pages/public/InternshipDirectoryPage';
import { AboutPage, ContactPage } from './pages/public/AboutPage';
import { LoginPage } from './pages/public/LoginPage';

// Portal Views
import { DashboardView } from './pages/portal/DashboardView';
import { StudentsManager } from './pages/portal/StudentsManager';
import { InternshipsManager } from './pages/portal/InternshipsManager';
import { ExcelImportManager } from './pages/portal/ExcelImportManager';
import { PdfUploadManager } from './pages/portal/PdfUploadManager';
import { ReportsManager } from './pages/portal/ReportsManager';
import { AdminImportApprovals } from './pages/portal/AdminImportApprovals';
import { AdminClientAccounts } from './pages/portal/AdminClientAccounts';
import { AdminPublicPermissions } from './pages/portal/AdminPublicPermissions';
import { AdminAuditLogs } from './pages/portal/AdminAuditLogs';
import { AdminSettings } from './pages/portal/AdminSettings';

const AppContent: React.FC = () => {
  const { user, loading } = useAuth();
  const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
  const [currentView, setCurrentView] = useState<string>(() => {
    return urlParams?.get('view') || 'home';
  });
  const [currentPortalTab, setCurrentPortalTab] = useState<string>(() => {
    return urlParams?.get('tab') || 'dashboard';
  });
  const [selectedRollNo, setSelectedRollNo] = useState<string | null>(null);

  const isPortalRequested = currentView === 'client-dashboard' || currentView === 'admin-dashboard' || currentView === 'portal';
  const isPortalView = Boolean(user) && isPortalRequested;
  const roleUpper = user?.role?.toUpperCase() || '';
  const isAdmin = true;

  React.useEffect(() => {
    if (!loading && !user && isPortalRequested) {
      setCurrentView('home');
    }
  }, [loading, user, isPortalRequested]);

  // Lenis smooth scroll for public views, cleanly disabled for portal views and data tables
  useSmoothScroll(!isPortalView);

  return (
    <div className="min-h-screen flex flex-col bg-white text-[#1D1D1F]">
      {!isPortalView ? (
        // Public Website Layout
        <>
          <Navbar
            currentView={currentView}
            setCurrentView={setCurrentView}
            setSelectedRollNo={setSelectedRollNo}
          />
          <main className="flex-1">
            {currentView === 'home' && (
              <HomePage
                setCurrentView={setCurrentView}
                setSelectedRollNo={(roll) => {
                  setSelectedRollNo(roll);
                  setCurrentView('student-profile');
                }}
              />
            )}
            {currentView === 'student-directory' && (
              <StudentDirectoryPage
                setSelectedRollNo={(roll) => {
                  setSelectedRollNo(roll);
                  setCurrentView('student-profile');
                }}
                setCurrentView={setCurrentView}
              />
            )}
            {currentView === 'student-profile' && selectedRollNo && (
              <PublicStudentProfilePage
                rollNo={selectedRollNo}
                setCurrentView={setCurrentView}
              />
            )}
            {currentView === 'internship-directory' && (
              <InternshipDirectoryPage />
            )}
            {currentView === 'about' && (
              <AboutPage />
            )}
            {currentView === 'contact' && (
              <ContactPage />
            )}
            {(currentView === 'admin-login' || currentView === 'client-login' || currentView === 'login') && (
              <LoginPage
                initialRole="admin"
                setCurrentView={setCurrentView}
              />
            )}
          </main>
          <Footer setCurrentView={setCurrentView} />
        </>
      ) : (
        // Portal Dashboard Layout (Client or Admin)
        <PortalLayout
          currentTab={currentPortalTab}
          setCurrentTab={setCurrentPortalTab}
          setCurrentView={setCurrentView}
        >
          {currentPortalTab === 'dashboard' && (
            <DashboardView setCurrentTab={setCurrentPortalTab} isAdmin={isAdmin} />
          )}
          {currentPortalTab === 'students' && (
            <StudentsManager isAdmin={isAdmin} />
          )}
          {currentPortalTab === 'internships' && (
            <InternshipsManager isAdmin={isAdmin} />
          )}
          {currentPortalTab === 'excel-import' && (
            <ExcelImportManager />
          )}
          {currentPortalTab === 'pdf-upload' && (
            <PdfUploadManager />
          )}
          {currentPortalTab === 'reports' && (
            <ReportsManager />
          )}
          {isAdmin && currentPortalTab === 'import-approvals' && (
            <AdminImportApprovals />
          )}
          {isAdmin && currentPortalTab === 'clients' && (
            <AdminClientAccounts />
          )}
          {isAdmin && currentPortalTab === 'permissions' && (
            <AdminPublicPermissions />
          )}
          {isAdmin && currentPortalTab === 'audit-logs' && (
            <AdminAuditLogs />
          )}
          {isAdmin && currentPortalTab === 'settings' && (
            <AdminSettings />
          )}
        </PortalLayout>
      )}
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
