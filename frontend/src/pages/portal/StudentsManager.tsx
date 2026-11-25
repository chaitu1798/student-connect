import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Plus,
  Edit3,
  Trash2,
  Eye,
  Upload,
  X,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  Camera,
  CreditCard,
  ShieldCheck,
  Mail,
  Phone,
  GraduationCap,
  Award,
  BookOpen,
  RotateCcw,
  Building,
  CheckCircle2,
  Calendar,
  MapPin,
  ExternalLink,
  Filter
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { Student } from '../../types';
import { AssetoCard } from '../../components/ui/AssetoCard';
import { StudentAvatar } from '../../components/ui/StudentAvatar';

export const StudentsManager: React.FC<{ isAdmin?: boolean }> = ({ isAdmin }) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);
  const [search, setSearch] = useState('');
  const [branchFilter, setBranchFilter] = useState('');
  const [loading, setLoading] = useState(false);

  // Student Details View Modal (All 41 credentials)
  const [viewModalOpen, setViewModalOpen] = useState(false);
  const [viewStudent, setViewStudent] = useState<Student | null>(null);
  const [modalActiveTab, setModalActiveTab] = useState<'academic' | 'contact' | 'personal' | 'secondary' | 'admission' | 'docs'>('academic');

  // Add / Edit Modal states
  const [modalOpen, setModalOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentStudent, setCurrentStudent] = useState<Partial<Student>>({});
  const [editTab, setEditTab] = useState<'academic' | 'contact' | 'personal' | 'schooling' | 'admission' | 'docs'>('academic');
  const [modalSaving, setModalSaving] = useState(false);
  const [modalError, setModalError] = useState('');

  // Delete modal
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [studentToDelete, setStudentToDelete] = useState<Student | null>(null);
  const [deleting, setDeleting] = useState(false);

  // Upload modal for Aadhaar / Passport Photo
  const [docUploadOpen, setDocUploadOpen] = useState(false);
  const [docTargetRoll, setDocTargetRoll] = useState('');
  const [docType, setDocType] = useState<'photo' | 'aadhaar'>('photo');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [photoTimestamp, setPhotoTimestamp] = useState<number>(Date.now());

  const fetchStudents = () => {
    setLoading(true);
    let url = `/students?page=${page}&page_size=${pageSize}`;
    if (search.trim()) url += `&search=${encodeURIComponent(search.trim())}`;
    if (branchFilter) url += `&branch=${encodeURIComponent(branchFilter)}`;

    apiClient.get(url)
      .then((res) => {
        setStudents(res.data.items || []);
        setTotal(res.data.total || 0);
      })
      .catch((err) => console.error('Error fetching students:', err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchStudents();
  }, [page, branchFilter]);

  // Open details modal if ?roll= query param is provided
  useEffect(() => {
    const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    const targetRoll = urlParams?.get('roll');
    if (targetRoll && students.length > 0) {
      const target = students.find((s) => s.roll_no === targetRoll);
      if (target) {
        if (urlParams?.get('action') === 'edit') {
          handleOpenEdit(target);
        } else {
          setViewStudent(target);
          setViewModalOpen(true);
        }
      }
    }
  }, [students]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchStudents();
  };

  const handleResetFilters = () => {
    setSearch('');
    setBranchFilter('');
    setPage(1);
  };

  const handleOpenView = (student: Student) => {
    setViewStudent(student);
    setModalActiveTab('academic');
    setViewModalOpen(true);
  };

  const handleOpenAdd = () => {
    setCurrentStudent({
      s_no: String(total + 1),
      roll_no: '',
      full_name: '',
      first_name: '',
      middle_name: '',
      last_name: '',
      branch: 'Computer Science & Engineering',
      branch_code: 'CSE',
      name_of_college: "Vignan's Institute Of Information Technology",
      column1: 'Placement Eligible',
      ug_cgpa: 8.0,
      ug_year_of_passing: 2025,
      number_of_backlogs: 0,
      crt_registered: 'Y',
      recorded_email: '',
      corrected_placement_email: '',
      alternate_personal_email: '',
      contact_number: '',
      parent_contact_number: '',
      full_residential_address: '',
      gender: 'Male',
      date_of_birth: '',
      father_name: '',
      father_occupation: '',
      languages_known: 'English, Telugu, Hindi',
      caste: 'General / OC',
      pan_number: '',
      aadhaar_number: '',
      x_grading_system: 'CGPA (10 pt)',
      x_cgpa_percentage: '',
      x_year_of_passing: 2019,
      x_school_name: '',
      study_after_x: 'Intermediate',
      xii_grading_system: 'Percentage / Marks',
      xii_cgpa_percentage: '',
      xii_year_of_passing: 2021,
      xii_college_name: '',
      admission_type: 'Convenor Quota (Govt)',
      entrance_exam: 'EAPCET',
      entrance_rank: '',
    });
    setEditMode(false);
    setEditTab('academic');
    setModalError('');
    setModalOpen(true);
  };

  const handleOpenEdit = (student: Student) => {
    setCurrentStudent({
      ...student,
      contact_number: student.contact_number || student.contact_no || '',
      parent_contact_number: student.parent_contact_number || student.parent_contact_no || '',
      corrected_placement_email: student.corrected_placement_email || student.corrected_placements_email || '',
      ug_year_of_passing: student.ug_year_of_passing || student.ug_year_of_pass || 2025,
      number_of_backlogs: student.number_of_backlogs ?? student.no_of_backlogs ?? 0,
      full_residential_address: student.full_residential_address || student.residential_address || '',
      x_year_of_passing: student.x_year_of_passing || student.x_year_of_pass || undefined,
      xii_year_of_passing: student.xii_year_of_passing || student.xii_year_of_pass || undefined,
      xii_cgpa_percentage: student.xii_cgpa_percentage || student.xii_percentage_cgpa || '',
    });
    setEditMode(true);
    setEditTab('academic');
    setModalError('');
    setModalOpen(true);
  };

  const handleSaveStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentStudent.roll_no || !currentStudent.full_name) {
      setModalError('Roll number and Full Name are mandatory fields.');
      return;
    }
    setModalSaving(true);
    setModalError('');
    try {
      if (editMode) {
        const res = await apiClient.patch(`/students/${encodeURIComponent(currentStudent.roll_no)}`, currentStudent);
        // Update local state
        setStudents(students.map((s) => (s.roll_no === currentStudent.roll_no ? res.data : s)));
        if (viewStudent && viewStudent.roll_no === currentStudent.roll_no) {
          setViewStudent(res.data);
        }
      } else {
        const res = await apiClient.post('/students', currentStudent);
        setStudents([res.data, ...students]);
        setTotal(total + 1);
      }
      setModalOpen(false);
    } catch (err: any) {
      console.error('Error saving student:', err);
      setModalError(err.response?.data?.detail || 'Failed to save student record.');
    } finally {
      setModalSaving(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!studentToDelete) return;
    setDeleting(true);
    try {
      await apiClient.delete(`/students/${encodeURIComponent(studentToDelete.roll_no)}`);
      setStudents(students.filter((s) => s.roll_no !== studentToDelete.roll_no));
      setTotal(Math.max(0, total - 1));
      setDeleteConfirmOpen(false);
      setStudentToDelete(null);
      if (viewModalOpen && viewStudent?.roll_no === studentToDelete.roll_no) {
        setViewModalOpen(false);
      }
    } catch (err: any) {
      console.error('Error deleting student:', err);
      alert(err.response?.data?.detail || 'Failed to delete student.');
    } finally {
      setDeleting(false);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !docTargetRoll) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('doc_type', docType);

    try {
      const res = await apiClient.post(`/documents/student/${encodeURIComponent(docTargetRoll)}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      const newTimestamp = Date.now();
      setPhotoTimestamp(newTimestamp);

      // Refresh student in list and in modal
      if (viewStudent && viewStudent.roll_no === docTargetRoll) {
        if (docType === 'photo') {
          setViewStudent({ ...viewStudent, photo_image_path: res.data.photo_image_path || res.data.path });
        } else {
          setViewStudent({ ...viewStudent, aadhaar_image_path: res.data.aadhaar_image_path || res.data.path });
        }
      }

      setStudents(
        students.map((s) => {
          if (s.roll_no === docTargetRoll) {
            return {
              ...s,
              photo_image_path: docType === 'photo' ? res.data.photo_image_path || res.data.path : s.photo_image_path,
              aadhaar_image_path: docType === 'aadhaar' ? res.data.aadhaar_image_path || res.data.path : s.aadhaar_image_path,
            };
          }
          return s;
        })
      );

      setDocUploadOpen(false);
      setUploadFile(null);
    } catch (err: any) {
      console.error('Upload error:', err);
      alert(err.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6 max-w-[1500px] mx-auto pb-12 font-sans">
      {/* Header and Search/Filter Controls Card */}
      <div className="bg-white border border-[#E8ECEF] rounded-2xl p-6 shadow-[0_1px_3px_0_rgba(22,40,59,0.04)]">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-[#1758A2] mb-1">
              <span className="w-2 h-2 rounded-full bg-[#1758A2]"></span>
              <span>Student Records Directory</span>
              <span>•</span>
              <span className="text-[#64748B] font-normal">{total} Enrolled Profiles</span>
            </div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#16283B]">
              Student Directory Management
            </h1>
            <p className="text-xs text-[#64748B] mt-1">
              Browse, search, edit, verify 41 student credentials, and manage passport photographs.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleOpenAdd}
              className="asseto-btn-primary text-xs py-2 px-4 rounded-xl"
            >
              <Plus className="w-4 h-4" />
              <span>Register New Student</span>
            </button>
          </div>
        </div>

        {/* Search & Filter Bar */}
        <div className="mt-5 pt-4 border-t border-[#F1F4F7] flex flex-col md:flex-row items-center gap-3">
          <form onSubmit={handleSearchSubmit} className="flex-1 w-full relative">
            <Search className="w-4 h-4 text-[#94A3B8] absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by student name or roll number (e.g. 21A91A0501)..."
              className="w-full pl-9 pr-24 py-2 text-xs bg-[#F6F6F6] hover:bg-[#F1F4F7] focus:bg-white border border-[#E8ECEF] focus:border-[#1758A2] rounded-xl outline-none transition text-[#16283B]"
            />
            <button
              type="submit"
              className="absolute right-1.5 top-1/2 -translate-y-1/2 px-3 py-1 bg-[#1758A2] text-white text-xs font-semibold rounded-lg hover:bg-[#124580] transition"
            >
              Search
            </button>
          </form>

          {/* Branch filter dropdown */}
          <div className="w-full md:w-56 shrink-0">
            <select
              value={branchFilter}
              onChange={(e) => {
                setBranchFilter(e.target.value);
                setPage(1);
              }}
              className="w-full py-2 px-3 text-xs bg-[#F6F6F6] border border-[#E8ECEF] focus:border-[#1758A2] rounded-xl outline-none text-[#16283B]"
            >
              <option value="">All Academic Departments</option>
              <option value="Computer Science">Computer Science (CSE)</option>
              <option value="Electronics">Electronics & Comm (ECE)</option>
              <option value="Information Technology">Information Tech (IT)</option>
              <option value="Electrical">Electrical & Electronics (EEE)</option>
              <option value="Mechanical">Mechanical Engineering (MECH)</option>
              <option value="Civil">Civil Engineering (CIVIL)</option>
              <option value="Artificial Intelligence">AI & Data Science (AI_DS)</option>
            </select>
          </div>

          {(search || branchFilter) && (
            <button
              onClick={handleResetFilters}
              className="p-2 text-[#64748B] hover:text-[#16283B] hover:bg-[#F1F4F7] rounded-xl transition text-xs shrink-0 flex items-center gap-1.5"
              title="Reset search and filters"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset</span>
            </button>
          )}
        </div>
      </div>

      {/* Asseto Student Directory Table Card */}
      <AssetoCard noPadding>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-[#F8FAFC] border-b border-[#E8ECEF] text-[11px] font-semibold text-[#64748B] uppercase tracking-wider">
                <th className="py-3 px-4">Student Profile</th>
                <th className="py-3 px-4">Department & College</th>
                <th className="py-3 px-4">Contact Info</th>
                <th className="py-3 px-4">Academic Standing</th>
                <th className="py-3 px-4">Placements & CRT</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F4F7] text-xs">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center text-[#64748B]">
                    <div className="w-8 h-8 border-2 border-[#1758A2] border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                    <span>Loading student directory records...</span>
                  </td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-16 text-center text-[#64748B]">
                    <Users className="w-10 h-10 text-[#94A3B8] mx-auto mb-2 opacity-50" />
                    <p className="font-semibold text-sm text-[#16283B]">No student records found</p>
                    <p className="text-xs text-[#64748B] mt-1">Try resetting search filters or register a new student.</p>
                  </td>
                </tr>
              ) : (
                students.map((student) => {
                  const cgpa = student.ug_cgpa || 0;
                  const backlogs = student.number_of_backlogs || student.no_of_backlogs || 0;
                  const intCount = student.internship_count || 0;

                  return (
                    <tr
                      key={student.roll_no}
                      className="hover:bg-[#F8FAFC] transition group"
                    >
                      {/* Student Profile (Photo + Name + Roll No) */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <StudentAvatar
                            rollNo={student.roll_no}
                            name={student.full_name}
                            photoPath={student.photo_image_path}
                            size="md"
                            timestamp={photoTimestamp}
                          />
                          <div>
                            <button
                              onClick={() => handleOpenView(student)}
                              className="font-semibold text-[#16283B] hover:text-[#1758A2] transition text-left leading-tight"
                            >
                              {student.full_name}
                            </button>
                            <div className="flex items-center gap-1.5 mt-0.5">
                              <span className="font-mono text-[11px] font-semibold text-[#1758A2] bg-[#1758A2]/10 px-1.5 py-0.2 rounded">
                                {student.roll_no}
                              </span>
                              {student.gender && (
                                <span className="text-[10px] text-[#64748B]">
                                  • {student.gender}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Department & College */}
                      <td className="py-3.5 px-4">
                        <div className="font-medium text-[#16283B]">
                          {student.branch || 'General Engineering'}
                        </div>
                        <div className="text-[11px] text-[#64748B] truncate max-w-[200px]">
                          {student.name_of_college || "Vignan's Institute Of Information Technology"}
                        </div>
                      </td>

                      {/* Contact Info */}
                      <td className="py-3.5 px-4">
                        <div className="text-[#16283B] font-mono text-[11px]">
                          {student.recorded_email || student.alternate_personal_email || 'No email registered'}
                        </div>
                        <div className="text-[11px] text-[#64748B] mt-0.5">
                          {student.contact_number || student.contact_no || 'No phone registered'}
                        </div>
                      </td>

                      {/* Academic Standing */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-[#16283B]">
                            {cgpa > 0 ? `${cgpa.toFixed(2)} CGPA` : 'N/A'}
                          </span>
                          {backlogs > 0 ? (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 border border-rose-200">
                              {backlogs} Backlogs
                            </span>
                          ) : (
                            <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              0 Backlogs
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-[#64748B] mt-0.5">
                          Class of {student.ug_year_of_passing || student.ug_year_of_pass || '2025'}
                        </div>
                      </td>

                      {/* Placements & CRT */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                              intCount > 0
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-slate-100 text-slate-600 border border-slate-200'
                            }`}
                          >
                            {intCount > 0 ? `${intCount} Placed` : '0 Internships'}
                          </span>
                          {student.crt_registered === 'Y' && (
                            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-[#1758A2] border border-[#1758A2]/20">
                              CRT
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <button
                            onClick={() => handleOpenView(student)}
                            className="p-1.5 text-[#64748B] hover:text-[#1758A2] hover:bg-[#1758A2]/10 rounded-lg transition"
                            title="View complete 41-field credentials"
                          >
                            <Eye className="w-4 h-4" />
                          </button>

                          <button
                            onClick={() => {
                              setDocTargetRoll(student.roll_no);
                              setDocType('photo');
                              setDocUploadOpen(true);
                            }}
                            className="p-1.5 text-[#64748B] hover:text-emerald-700 hover:bg-emerald-50 rounded-lg transition"
                            title="Upload or replace photo"
                          >
                            <Camera className="w-4 h-4" />
                          </button>

                          <button
                            onClick={() => handleOpenEdit(student)}
                            className="p-1.5 text-[#64748B] hover:text-blue-700 hover:bg-blue-50 rounded-lg transition"
                            title="Edit student record"
                          >
                            <Edit3 className="w-4 h-4" />
                          </button>

                          {isAdmin && (
                            <button
                              onClick={() => {
                                setStudentToDelete(student);
                                setDeleteConfirmOpen(true);
                              }}
                              className="p-1.5 text-[#64748B] hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                              title="Delete student record"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="px-6 py-4 border-t border-[#F1F4F7] flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[#64748B]">
          <div>
            Showing <span className="font-semibold text-[#16283B]">{total > 0 ? (page - 1) * pageSize + 1 : 0}</span> to{' '}
            <span className="font-semibold text-[#16283B]">{Math.min(page * pageSize, total)}</span> of{' '}
            <span className="font-semibold text-[#16283B]">{total}</span> student records
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setPage(Math.max(1, page - 1))}
              disabled={page <= 1}
              className="px-3 py-1.5 rounded-lg border border-[#E8ECEF] bg-white text-[#16283B] hover:bg-[#F8FAFC] disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              Previous
            </button>
            <span className="px-3 py-1 font-semibold text-[#16283B]">
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => setPage(Math.min(totalPages, page + 1))}
              disabled={page >= totalPages}
              className="px-3 py-1.5 rounded-lg border border-[#E8ECEF] bg-white text-[#16283B] hover:bg-[#F8FAFC] disabled:opacity-40 disabled:cursor-not-allowed transition"
            >
              Next
            </button>
          </div>
        </div>
      </AssetoCard>

      {/* ========================================================================= */}
      {/* 41-FIELD STUDENT PROFILE DETAILS MODAL (Asseto Premium Experience) */}
      {/* ========================================================================= */}
      {viewModalOpen && viewStudent && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 z-50 animate-in fade-in duration-150">
          <div className="bg-white border border-[#E8ECEF] rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden font-sans">
            {/* Modal Top Bar */}
            <div className="px-6 py-4 border-b border-[#F1F4F7] flex items-center justify-between bg-white shrink-0">
              <div className="flex items-center gap-2">
                <span className="asseto-badge-blue">Official Student Credential Record</span>
                <span className="text-xs text-[#64748B]">ID: {viewStudent.id}</span>
              </div>
              <button
                onClick={() => setViewModalOpen(false)}
                className="p-1.5 text-[#64748B] hover:text-[#16283B] hover:bg-[#F1F4F7] rounded-xl transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="overflow-y-auto flex-1 p-6 space-y-6">
              {/* Profile Hero Header Card */}
              <div className="bg-[#F8FAFC] border border-[#E8ECEF] rounded-2xl p-5 flex flex-col sm:flex-row items-center sm:items-start gap-5">
                <div className="relative group shrink-0">
                  <StudentAvatar
                    rollNo={viewStudent.roll_no}
                    name={viewStudent.full_name}
                    photoPath={viewStudent.photo_image_path}
                    size="xl"
                    timestamp={photoTimestamp}
                  />
                  <button
                    onClick={() => {
                      setDocTargetRoll(viewStudent.roll_no);
                      setDocType('photo');
                      setDocUploadOpen(true);
                    }}
                    className="absolute -bottom-1 -right-1 p-1.5 bg-[#1758A2] text-white rounded-full hover:bg-[#124580] transition shadow-xs"
                    title="Change student photograph"
                  >
                    <Camera className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="flex-1 text-center sm:text-left min-w-0">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <h2 className="text-xl font-bold text-[#16283B] tracking-tight">
                        {viewStudent.full_name}
                      </h2>
                      <div className="flex items-center justify-center sm:justify-start gap-2 mt-1 flex-wrap">
                        <span className="font-mono text-xs font-bold text-[#1758A2] bg-[#1758A2]/10 px-2 py-0.5 rounded-md">
                          {viewStudent.roll_no}
                        </span>
                        <span className="text-xs font-semibold text-[#16283B]">
                          {viewStudent.branch || 'Engineering Department'}
                        </span>
                        <span className="text-xs text-[#64748B]">
                          • {viewStudent.branch_code || 'B.Tech'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-center sm:justify-end gap-2 shrink-0">
                      <button
                        onClick={() => {
                          handleOpenEdit(viewStudent);
                          setViewModalOpen(false);
                        }}
                        className="asseto-btn-secondary text-xs py-1.5 px-3 rounded-xl"
                      >
                        <Edit3 className="w-3.5 h-3.5 text-[#64748B]" />
                        <span>Edit Credentials</span>
                      </button>
                    </div>
                  </div>

                  {/* Highlights Bar */}
                  <div className="mt-4 pt-3 border-t border-[#E8ECEF] grid grid-cols-2 sm:grid-cols-4 gap-3 text-center sm:text-left text-xs">
                    <div>
                      <div className="text-[10px] text-[#64748B] uppercase font-medium">UG CGPA</div>
                      <div className="font-bold text-[#16283B] text-sm">
                        {viewStudent.ug_cgpa ? `${viewStudent.ug_cgpa.toFixed(2)}` : 'Not recorded'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-[#64748B] uppercase font-medium">Graduation Year</div>
                      <div className="font-bold text-[#16283B] text-sm">
                        {viewStudent.ug_year_of_passing || viewStudent.ug_year_of_pass || '2025'}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-[#64748B] uppercase font-medium">Active Backlogs</div>
                      <div className="font-bold text-[#16283B] text-sm">
                        {viewStudent.number_of_backlogs || viewStudent.no_of_backlogs || 0}
                      </div>
                    </div>
                    <div>
                      <div className="text-[10px] text-[#64748B] uppercase font-medium">CRT Placement</div>
                      <div className="font-bold text-[#1758A2] text-sm">
                        {viewStudent.crt_registered === 'Y' ? 'Enrolled' : 'Not Registered'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Navigation Tabs for the 41 Attributes */}
              <div className="flex items-center gap-1.5 border-b border-[#E8ECEF] overflow-x-auto pb-px">
                {[
                  { id: 'academic', label: 'UG Academic Standing' },
                  { id: 'contact', label: 'Contact & Addresses' },
                  { id: 'personal', label: 'Personal & Family' },
                  { id: 'secondary', label: '10th & 12th Schooling' },
                  { id: 'admission', label: 'Entrance & Quota' },
                  { id: 'docs', label: 'Identity & Photos' },
                ].map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setModalActiveTab(t.id as any)}
                    className={`px-3.5 py-2 text-xs font-semibold rounded-t-xl transition shrink-0 ${
                      modalActiveTab === t.id
                        ? 'border-b-2 border-[#1758A2] text-[#1758A2] bg-white'
                        : 'text-[#64748B] hover:text-[#16283B] hover:bg-[#F8FAFC]'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>

              {/* Tab 1: UG Academic Credentials */}
              {modalActiveTab === 'academic' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">1. Serial No</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.s_no || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">2. Roll Number</div>
                    <div className="font-mono font-bold text-[#1758A2] mt-0.5">{viewStudent.roll_no}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">3. Full Name (SSC)</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.full_name}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">4. Branch / Stream</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.branch || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">5. Branch Code</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.branch_code || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">6. Institution / College</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.name_of_college || "Vignan's Institute Of Information Technology"}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">7. UG Cumulative CGPA</div>
                    <div className="font-bold text-[#16283B] mt-0.5">{viewStudent.ug_cgpa ? `${viewStudent.ug_cgpa.toFixed(2)} / 10.0` : 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">8. Year of Passing</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.ug_year_of_passing || viewStudent.ug_year_of_pass || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">9. Active Backlogs Count</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.number_of_backlogs || viewStudent.no_of_backlogs || 0}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">10. CRT Registered</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.crt_registered === 'Y' ? 'Yes (Enrolled)' : 'No'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">11. Total Internships</div>
                    <div className="font-semibold text-[#1758A2] mt-0.5">{viewStudent.internship_count || 0} Verified</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">12. Legacy Column 1</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.column1 || 'N/A'}</div>
                  </div>
                </div>
              )}

              {/* Tab 2: Contact Information & Addresses */}
              {modalActiveTab === 'contact' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">13. Recorded Official Email</div>
                    <div className="font-mono text-[#16283B] mt-0.5">{viewStudent.recorded_email || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">14. Corrected Placement Email</div>
                    <div className="font-mono text-[#16283B] mt-0.5">{viewStudent.corrected_placement_email || viewStudent.corrected_placements_email || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">15. Alternate Personal Email</div>
                    <div className="font-mono text-[#16283B] mt-0.5">{viewStudent.alternate_personal_email || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">16. Primary Contact Number</div>
                    <div className="font-mono text-[#16283B] mt-0.5">{viewStudent.contact_number || viewStudent.contact_no || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">17. Parent Contact Number</div>
                    <div className="font-mono text-[#16283B] mt-0.5">{viewStudent.parent_contact_number || viewStudent.parent_contact_no || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF] sm:col-span-2">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">18. Full Residential Address</div>
                    <div className="text-[#16283B] mt-0.5">{viewStudent.full_residential_address || viewStudent.residential_address || 'N/A'}</div>
                  </div>
                </div>
              )}

              {/* Tab 3: Personal & Family */}
              {modalActiveTab === 'personal' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">19. Gender</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.gender || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">20. Date of Birth</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.date_of_birth || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">21. Languages Known</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.languages_known || 'English, Telugu, Hindi'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">22. Father's Name</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.father_name || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">23. Father's Occupation</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.father_occupation || 'N/A'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">24. Caste / Category</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.caste || 'General / OC'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">25. PAN Card Number</div>
                    <div className="font-mono font-semibold text-[#16283B] mt-0.5">{viewStudent.pan_number || '•••• •••• ••••'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">26. Aadhaar Number</div>
                    <div className="font-mono font-semibold text-[#16283B] mt-0.5">{viewStudent.aadhaar_number || '•••• •••• ••••'}</div>
                  </div>
                </div>
              )}

              {/* Tab 4: Secondary (10th) & Intermediate (12th) */}
              {modalActiveTab === 'secondary' && (
                <div className="space-y-4 text-xs">
                  <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E8ECEF]">
                    <h4 className="font-bold text-[#16283B] mb-3">Secondary School Certificate (Grade X)</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                      <div>
                        <div className="text-[10px] text-[#64748B]">27. Grading System</div>
                        <div className="font-semibold text-[#16283B]">{viewStudent.x_grading_system || 'CGPA (10 pt)'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">28. CGPA / Percentage</div>
                        <div className="font-bold text-[#16283B]">{viewStudent.x_cgpa_percentage || '9.8 / 10.0'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">29. Year of Passing</div>
                        <div className="font-semibold text-[#16283B]">{viewStudent.x_year_of_passing || viewStudent.x_year_of_pass || '2019'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">30. School Name</div>
                        <div className="font-semibold text-[#16283B] truncate">{viewStudent.x_school_name || 'Public High School'}</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E8ECEF]">
                    <h4 className="font-bold text-[#16283B] mb-3">Higher Secondary / Intermediate / Diploma (Grade XII)</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
                      <div>
                        <div className="text-[10px] text-[#64748B]">31. Study Path</div>
                        <div className="font-semibold text-[#16283B]">{viewStudent.study_after_x || 'Intermediate'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">32. Grading System</div>
                        <div className="font-semibold text-[#16283B]">{viewStudent.xii_grading_system || 'Percentage / Marks'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">33. Percentage / CGPA</div>
                        <div className="font-bold text-[#16283B]">{viewStudent.xii_cgpa_percentage || viewStudent.xii_percentage_cgpa || '96.2%'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">34. Year of Passing</div>
                        <div className="font-semibold text-[#16283B]">{viewStudent.xii_year_of_passing || viewStudent.xii_year_of_pass || '2021'}</div>
                      </div>
                      <div>
                        <div className="text-[10px] text-[#64748B]">35. Junior College</div>
                        <div className="font-semibold text-[#16283B] truncate">{viewStudent.xii_college_name || 'Junior College of Science'}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 5: Admission & Entrance */}
              {modalActiveTab === 'admission' && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">36. Admission Type / Quota</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.admission_type || 'Convenor Quota (Govt)'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">37. Entrance Exam Taken</div>
                    <div className="font-semibold text-[#16283B] mt-0.5">{viewStudent.entrance_exam || 'EAPCET / JEE Main'}</div>
                  </div>
                  <div className="p-3.5 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF]">
                    <div className="text-[10px] uppercase font-medium text-[#64748B]">38. Entrance Rank</div>
                    <div className="font-bold text-[#1758A2] mt-0.5">{viewStudent.entrance_rank || 'State Rank #4,120'}</div>
                  </div>
                </div>
              )}

              {/* Tab 6: Identity Documents & Photos */}
              {modalActiveTab === 'docs' && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
                  {/* Passport Photo */}
                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E8ECEF] flex flex-col items-center text-center space-y-3">
                    <div className="font-bold text-sm text-[#16283B]">Field 41: Verified Passport Photograph</div>
                    <StudentAvatar
                      rollNo={viewStudent.roll_no}
                      name={viewStudent.full_name}
                      photoPath={viewStudent.photo_image_path}
                      size="2xl"
                      timestamp={photoTimestamp}
                    />
                    <div className="text-[11px] text-[#64748B]">
                      {viewStudent.photo_image_path ? `File: ${viewStudent.photo_image_path}` : 'No custom photo uploaded. Showing fallback avatar.'}
                    </div>
                    <button
                      onClick={() => {
                        setDocTargetRoll(viewStudent.roll_no);
                        setDocType('photo');
                        setDocUploadOpen(true);
                      }}
                      className="asseto-btn-primary text-xs py-1.5 px-4 rounded-xl"
                    >
                      <Camera className="w-4 h-4" />
                      <span>Upload New Photo</span>
                    </button>
                  </div>

                  {/* Aadhaar Document Preview */}
                  <div className="p-5 rounded-2xl bg-[#F8FAFC] border border-[#E8ECEF] flex flex-col items-center text-center space-y-3">
                    <div className="font-bold text-sm text-[#16283B]">Aadhaar Card Identification</div>
                    <div className="w-44 h-28 rounded-xl bg-slate-200 border border-[#E8ECEF] overflow-hidden flex items-center justify-center relative">
                      {viewStudent.aadhaar_image_path ? (
                        <img
                          src={`/api/v1/documents/view?path=${encodeURIComponent(viewStudent.aadhaar_image_path)}`}
                          alt="Aadhaar Document"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="text-[11px] text-[#64748B] flex flex-col items-center gap-1 p-2">
                          <CreditCard className="w-6 h-6 text-[#94A3B8]" />
                          <span>Protected Aadhaar file</span>
                        </div>
                      )}
                    </div>
                    <div className="text-[11px] text-[#64748B]">
                      {viewStudent.aadhaar_number ? `Masked ID: ${viewStudent.aadhaar_number}` : 'Identity document registered'}
                    </div>
                    <button
                      onClick={() => {
                        setDocTargetRoll(viewStudent.roll_no);
                        setDocType('aadhaar');
                        setDocUploadOpen(true);
                      }}
                      className="asseto-btn-secondary text-xs py-1.5 px-4 rounded-xl"
                    >
                      <Upload className="w-4 h-4" />
                      <span>Replace Aadhaar Card</span>
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-[#F1F4F7] bg-[#FAFAFA] flex items-center justify-between shrink-0">
              <span className="text-[11px] text-[#64748B]">
                All 41 credentials synchronized with PostgreSQL/SQLite master schema.
              </span>
              <button
                onClick={() => setViewModalOpen(false)}
                className="asseto-btn-secondary text-xs py-1.5 px-4 rounded-xl"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* ADD / EDIT STUDENT MODAL */}
      {/* ========================================================================= */}
      {/* ========================================================================= */}
      {/* ADD / EDIT STUDENT MODAL — FULL 41 ATTRIBUTES */}
      {/* ========================================================================= */}
      {modalOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-3 sm:p-4 z-50 animate-in fade-in duration-150">
          <div className="bg-white border border-[#E8ECEF] rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden font-sans">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-[#F1F4F7] flex items-center justify-between shrink-0 bg-[#FAFAFA]">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#1758A2]"></span>
                  <h3 className="text-base font-bold text-[#16283B]">
                    {editMode ? `Edit Student: ${currentStudent.roll_no}` : 'Register New Student Profile'}
                  </h3>
                  {editMode && currentStudent.branch && (
                    <span className="text-[11px] font-semibold text-[#1758A2] bg-[#1758A2]/10 px-2 py-0.5 rounded-md">
                      {currentStudent.branch_code || currentStudent.branch}
                    </span>
                  )}
                </div>
                <p className="text-xs text-[#64748B] mt-0.5">
                  {editMode
                    ? `Modifying verified institutional credential records for ${currentStudent.full_name || 'student'}.`
                    : 'Enter all 41 academic, personal, schooling, and contact attributes.'}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="p-1.5 text-[#64748B] hover:text-[#16283B] rounded-xl hover:bg-[#F0F3F6] transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Edit Tab Navigation (All 6 Logical Groups) */}
            <div className="px-6 pt-3 pb-2 border-b border-[#E8ECEF] flex items-center gap-1.5 overflow-x-auto text-xs shrink-0 bg-white">
              {[
                { id: 'academic', label: 'UG Academic Standing', icon: GraduationCap },
                { id: 'contact', label: 'Contact & Addresses', icon: Mail },
                { id: 'personal', label: 'Personal & Family', icon: Users },
                { id: 'schooling', label: '10th & 12th Schooling', icon: BookOpen },
                { id: 'admission', label: 'Entrance & Quota', icon: Award },
                { id: 'docs', label: 'Identity & Photos', icon: Camera },
              ].map((t) => {
                const Icon = t.icon;
                const isActive = editTab === t.id;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setEditTab(t.id as any)}
                    className={`px-3 py-1.5 rounded-xl font-semibold flex items-center gap-1.5 transition whitespace-nowrap ${
                      isActive
                        ? 'bg-[#1758A2] text-white shadow-xs'
                        : 'text-[#64748B] hover:bg-[#F8FAFC] hover:text-[#16283B]'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>

            <form onSubmit={handleSaveStudent} className="flex-1 overflow-y-auto p-6 space-y-5">
              {modalError && (
                <div className="p-3 bg-rose-50 border border-rose-200 text-rose-800 text-xs rounded-xl flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{modalError}</span>
                </div>
              )}

              {/* TAB 1: UG Academic Standing (Fields 1-14) */}
              {editTab === 'academic' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">1. Serial Number</label>
                      <input
                        type="text"
                        value={currentStudent.s_no || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, s_no: e.target.value })}
                        placeholder="e.g. 1"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">
                        2. Roll Number * {editMode && <span className="text-[10px] text-[#64748B] font-normal">(Primary Key)</span>}
                      </label>
                      <input
                        type="text"
                        required
                        disabled={editMode}
                        value={currentStudent.roll_no || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, roll_no: e.target.value.toUpperCase() })}
                        placeholder="e.g. 21A91A0501"
                        className="w-full px-3 py-2 font-mono font-bold bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#1758A2] outline-none focus:border-[#1758A2] focus:bg-white transition disabled:opacity-75"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">3. Full Name (SSC) *</label>
                      <input
                        type="text"
                        required
                        value={currentStudent.full_name || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, full_name: e.target.value })}
                        placeholder="Full student legal name"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">4. First Name</label>
                      <input
                        type="text"
                        value={currentStudent.first_name || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, first_name: e.target.value })}
                        placeholder="First name"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">5. Middle Name</label>
                      <input
                        type="text"
                        value={currentStudent.middle_name || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, middle_name: e.target.value })}
                        placeholder="Middle name"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">6. Last Name</label>
                      <input
                        type="text"
                        value={currentStudent.last_name || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, last_name: e.target.value })}
                        placeholder="Last name / Surname"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">7. Branch / Department</label>
                      <select
                        value={currentStudent.branch || 'Computer Science & Engineering'}
                        onChange={(e) => {
                          const val = e.target.value;
                          let code = 'CSE';
                          if (val.includes('Electronics')) code = 'ECE';
                          else if (val.includes('Information')) code = 'IT';
                          else if (val.includes('Electrical')) code = 'EEE';
                          else if (val.includes('Mechanical')) code = 'MECH';
                          else if (val.includes('Civil')) code = 'CIVIL';
                          else if (val.includes('Artificial')) code = 'AIDS';
                          setCurrentStudent({ ...currentStudent, branch: val, branch_code: code });
                        }}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      >
                        <option value="Computer Science & Engineering">Computer Science & Engineering</option>
                        <option value="Electronics & Communication Engineering">Electronics & Communication Engineering</option>
                        <option value="Information Technology">Information Technology</option>
                        <option value="Electrical & Electronics Engineering">Electrical & Electronics Engineering</option>
                        <option value="Mechanical Engineering">Mechanical Engineering</option>
                        <option value="Civil Engineering">Civil Engineering</option>
                        <option value="Artificial Intelligence & Data Science">Artificial Intelligence & Data Science</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">8. Branch Code</label>
                      <input
                        type="text"
                        value={currentStudent.branch_code || 'CSE'}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, branch_code: e.target.value.toUpperCase() })}
                        placeholder="e.g. CSE, ECE"
                        className="w-full px-3 py-2 font-mono uppercase bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">9. Institution / College</label>
                      <input
                        type="text"
                        value={currentStudent.name_of_college || "Vignan's Institute Of Information Technology"}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, name_of_college: e.target.value })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">10. UG CGPA (0 - 10)</label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="10"
                        value={currentStudent.ug_cgpa ?? ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, ug_cgpa: parseFloat(e.target.value) || 0 })}
                        placeholder="e.g. 8.45"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">11. Year of Passing</label>
                      <input
                        type="number"
                        value={currentStudent.ug_year_of_passing || 2025}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, ug_year_of_passing: parseInt(e.target.value) || 2025 })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">12. Active Backlogs</label>
                      <input
                        type="number"
                        min="0"
                        value={currentStudent.number_of_backlogs ?? 0}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, number_of_backlogs: parseInt(e.target.value) || 0 })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">13. CRT Registered</label>
                      <select
                        value={currentStudent.crt_registered || 'Y'}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, crt_registered: e.target.value })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      >
                        <option value="Y">Yes (Enrolled)</option>
                        <option value="N">No (Not Enrolled)</option>
                      </select>
                    </div>
                  </div>

                  <div className="text-xs">
                    <label className="block text-[11px] font-semibold text-[#16283B] mb-1">14. Legacy Column 1 (Remarks / Notes)</label>
                    <input
                      type="text"
                      value={currentStudent.column1 || ''}
                      onChange={(e) => setCurrentStudent({ ...currentStudent, column1: e.target.value })}
                      placeholder="e.g. Placement Eligible, Fast-track, Special category"
                      className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                    />
                  </div>
                </div>
              )}

              {/* TAB 2: Contact & Addresses (Fields 15-20) */}
              {editTab === 'contact' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">15. Official Recorded Email</label>
                      <input
                        type="email"
                        value={currentStudent.recorded_email || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, recorded_email: e.target.value })}
                        placeholder="student@institution.edu"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">16. Corrected Placements Email</label>
                      <input
                        type="email"
                        value={currentStudent.corrected_placement_email || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, corrected_placement_email: e.target.value })}
                        placeholder="placement.official@gmail.com"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">17. Alternate Personal Email</label>
                      <input
                        type="email"
                        value={currentStudent.alternate_personal_email || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, alternate_personal_email: e.target.value })}
                        placeholder="personal.email@gmail.com"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">18. Student Mobile Number</label>
                      <input
                        type="tel"
                        value={currentStudent.contact_number || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, contact_number: e.target.value })}
                        placeholder="10-digit mobile number"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">19. Parent Mobile Number</label>
                      <input
                        type="tel"
                        value={currentStudent.parent_contact_number || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, parent_contact_number: e.target.value })}
                        placeholder="Parent / Guardian contact"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="text-xs">
                    <label className="block text-[11px] font-semibold text-[#16283B] mb-1">20. Full Residential Address</label>
                    <textarea
                      rows={3}
                      value={currentStudent.full_residential_address || ''}
                      onChange={(e) => setCurrentStudent({ ...currentStudent, full_residential_address: e.target.value })}
                      placeholder="Door No, Street, Landmark, Village/Town, Mandal, District, State, PIN"
                      className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                    ></textarea>
                  </div>
                </div>
              )}

              {/* TAB 3: Personal & Family Background (Fields 21-28) */}
              {editTab === 'personal' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">21. Gender</label>
                      <select
                        value={currentStudent.gender || 'Male'}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, gender: e.target.value })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      >
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">22. Date of Birth</label>
                      <input
                        type="date"
                        value={currentStudent.date_of_birth || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, date_of_birth: e.target.value })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">23. Father's Name</label>
                      <input
                        type="text"
                        value={currentStudent.father_name || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, father_name: e.target.value })}
                        placeholder="Father's full name"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">24. Father's Occupation</label>
                      <input
                        type="text"
                        value={currentStudent.father_occupation || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, father_occupation: e.target.value })}
                        placeholder="e.g. Agriculture, Business, Govt"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">25. Languages Known</label>
                      <input
                        type="text"
                        value={currentStudent.languages_known || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, languages_known: e.target.value })}
                        placeholder="English, Telugu, Hindi"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">26. Caste / Category</label>
                      <input
                        type="text"
                        value={currentStudent.caste || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, caste: e.target.value })}
                        placeholder="General / OC, BC-A, SC, ST, EWS"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">27. PAN Number</label>
                      <input
                        type="text"
                        value={currentStudent.pan_number || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, pan_number: e.target.value.toUpperCase() })}
                        placeholder="ABCDE1234F"
                        className="w-full px-3 py-2 font-mono uppercase bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">28. Aadhaar Number</label>
                      <input
                        type="text"
                        value={currentStudent.aadhaar_number || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, aadhaar_number: e.target.value })}
                        placeholder="12-digit Aadhaar number"
                        className="w-full px-3 py-2 font-mono bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 4: 10th (SSC) & 12th / Diploma Schooling (Fields 29-37) */}
              {editTab === 'schooling' && (
                <div className="space-y-5 text-xs">
                  {/* Grade X / SSC */}
                  <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E8ECEF] space-y-3">
                    <h4 className="font-bold text-[#16283B] flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#1758A2]"></span>
                      <span>Secondary School Certificate (Grade X)</span>
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">29. Grading System</label>
                        <select
                          value={currentStudent.x_grading_system || 'CGPA (10 pt)'}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, x_grading_system: e.target.value })}
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        >
                          <option value="CGPA (10 pt)">CGPA (10 pt)</option>
                          <option value="Percentage">Percentage (%)</option>
                          <option value="Marks (Out of 600)">Marks (Out of 600)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">30. CGPA / Percentage</label>
                        <input
                          type="text"
                          value={currentStudent.x_cgpa_percentage || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, x_cgpa_percentage: e.target.value })}
                          placeholder="e.g. 9.8 or 92%"
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">31. Year of Passing</label>
                        <input
                          type="number"
                          value={currentStudent.x_year_of_passing || 2019}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, x_year_of_passing: parseInt(e.target.value) || 2019 })}
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">32. School Name</label>
                        <input
                          type="text"
                          value={currentStudent.x_school_name || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, x_school_name: e.target.value })}
                          placeholder="e.g. Public High School"
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Grade XII / Intermediate / Diploma */}
                  <div className="bg-[#F8FAFC] p-4 rounded-xl border border-[#E8ECEF] space-y-3">
                    <h4 className="font-bold text-[#16283B] flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#1758A2]"></span>
                      <span>Higher Secondary / Intermediate / Diploma (Grade XII)</span>
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">33. Study Path After X</label>
                        <select
                          value={currentStudent.study_after_x || 'Intermediate'}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, study_after_x: e.target.value })}
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        >
                          <option value="Intermediate">Intermediate (10+2)</option>
                          <option value="Diploma">Polytechnic Diploma</option>
                          <option value="Vocational">Vocational</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">34. Grading System</label>
                        <select
                          value={currentStudent.xii_grading_system || 'Percentage / Marks'}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, xii_grading_system: e.target.value })}
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        >
                          <option value="Percentage / Marks">Percentage / Marks</option>
                          <option value="CGPA (10 pt)">CGPA (10 pt)</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">35. Percentage / CGPA</label>
                        <input
                          type="text"
                          value={currentStudent.xii_cgpa_percentage || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, xii_cgpa_percentage: e.target.value })}
                          placeholder="e.g. 96.2% or 9.5"
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">36. Year of Passing</label>
                        <input
                          type="number"
                          value={currentStudent.xii_year_of_passing || 2021}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, xii_year_of_passing: parseInt(e.target.value) || 2021 })}
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-semibold text-[#16283B] mb-1">37. Junior College Name</label>
                        <input
                          type="text"
                          value={currentStudent.xii_college_name || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, xii_college_name: e.target.value })}
                          placeholder="College / Institute name"
                          className="w-full px-3 py-2 bg-white border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 5: Entrance Exam & Admission Quota (Fields 38-40) */}
              {editTab === 'admission' && (
                <div className="space-y-4 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">38. Admission Type / Quota</label>
                      <select
                        value={currentStudent.admission_type || 'Convenor Quota (Govt)'}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, admission_type: e.target.value })}
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      >
                        <option value="Convenor Quota (Govt)">Convenor Quota (Govt)</option>
                        <option value="Management Quota">Management Quota</option>
                        <option value="Lateral Entry">Lateral Entry (ECET)</option>
                        <option value="NRI Quota">NRI Quota</option>
                        <option value="Sports / Special Quota">Sports / Special Quota</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">39. Entrance Exam Taken</label>
                      <input
                        type="text"
                        value={currentStudent.entrance_exam || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, entrance_exam: e.target.value })}
                        placeholder="e.g. EAPCET, JEE Main, ECET"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                    <div>
                      <label className="block text-[11px] font-semibold text-[#16283B] mb-1">40. Entrance Rank / Score</label>
                      <input
                        type="text"
                        value={currentStudent.entrance_rank || ''}
                        onChange={(e) => setCurrentStudent({ ...currentStudent, entrance_rank: e.target.value })}
                        placeholder="e.g. 4120 or 98.4 Percentile"
                        className="w-full px-3 py-2 bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl text-[#16283B] outline-none focus:border-[#1758A2] focus:bg-white transition"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 6: Identity Documents & Photos (Field 41) */}
              {editTab === 'docs' && (
                <div className="space-y-4 text-xs">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Passport Photo */}
                    <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF] flex flex-col items-center text-center space-y-3">
                      <div className="font-bold text-[#16283B]">41. Passport Photograph</div>
                      <StudentAvatar
                        rollNo={currentStudent.roll_no}
                        name={currentStudent.full_name}
                        photoPath={currentStudent.photo_image_path}
                        size="xl"
                        timestamp={photoTimestamp}
                      />
                      <div className="w-full space-y-2">
                        <label className="block text-[10px] text-[#64748B] text-left">Document File Path</label>
                        <input
                          type="text"
                          value={currentStudent.photo_image_path || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, photo_image_path: e.target.value })}
                          placeholder="photos/roll_photo.jpg"
                          className="w-full px-3 py-1.5 text-xs bg-white border border-[#E8ECEF] rounded-lg text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      {currentStudent.roll_no && (
                        <button
                          type="button"
                          onClick={() => {
                            setDocTargetRoll(currentStudent.roll_no || '');
                            setDocType('photo');
                            setDocUploadOpen(true);
                          }}
                          className="asseto-btn-primary text-xs py-1.5 px-3.5 rounded-xl w-full justify-center"
                        >
                          <Camera className="w-4 h-4" />
                          <span>Upload / Replace Photo File</span>
                        </button>
                      )}
                    </div>

                    {/* Aadhaar Card Document */}
                    <div className="p-4 rounded-xl bg-[#F8FAFC] border border-[#E8ECEF] flex flex-col items-center text-center space-y-3">
                      <div className="font-bold text-[#16283B]">Aadhaar Card Document (Private)</div>
                      <div className="w-16 h-16 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-500">
                        <CreditCard className="w-7 h-7" />
                      </div>
                      <div className="w-full space-y-2">
                        <label className="block text-[10px] text-[#64748B] text-left">Aadhaar Document Path</label>
                        <input
                          type="text"
                          value={currentStudent.aadhaar_image_path || ''}
                          onChange={(e) => setCurrentStudent({ ...currentStudent, aadhaar_image_path: e.target.value })}
                          placeholder="aadhaar/roll_aadhaar.jpg"
                          className="w-full px-3 py-1.5 text-xs bg-white border border-[#E8ECEF] rounded-lg text-[#16283B] outline-none focus:border-[#1758A2]"
                        />
                      </div>
                      {currentStudent.roll_no && (
                        <button
                          type="button"
                          onClick={() => {
                            setDocTargetRoll(currentStudent.roll_no || '');
                            setDocType('aadhaar');
                            setDocUploadOpen(true);
                          }}
                          className="asseto-btn-secondary text-xs py-1.5 px-3.5 rounded-xl w-full justify-center"
                        >
                          <ShieldCheck className="w-4 h-4 text-emerald-600" />
                          <span>Upload / Replace Aadhaar Card</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Modal Footer Controls */}
              <div className="pt-4 border-t border-[#F1F4F7] flex items-center justify-between gap-3 shrink-0">
                <div className="text-[11px] text-[#64748B]">
                  {editTab === 'academic' && 'Section 1 of 6: Undergraduate & Identity Details'}
                  {editTab === 'contact' && 'Section 2 of 6: Contact Numbers & Residential Address'}
                  {editTab === 'personal' && 'Section 3 of 6: Personal Background & Statutory Identifiers'}
                  {editTab === 'schooling' && 'Section 4 of 6: Secondary & Higher Secondary Schooling'}
                  {editTab === 'admission' && 'Section 5 of 6: Institutional Quota & Entrance Ranking'}
                  {editTab === 'docs' && 'Section 6 of 6: Official Photographs & Identity Documents'}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setModalOpen(false)}
                    className="asseto-btn-secondary text-xs py-2 px-4 rounded-xl"
                  >
                    Cancel
                  </button>

                  {/* Tab Stepper Helpers */}
                  {editTab !== 'docs' ? (
                    <button
                      type="button"
                      onClick={() => {
                        const tabs: Array<'academic' | 'contact' | 'personal' | 'schooling' | 'admission' | 'docs'> = [
                          'academic', 'contact', 'personal', 'schooling', 'admission', 'docs'
                        ];
                        const idx = tabs.indexOf(editTab);
                        if (idx < tabs.length - 1) setEditTab(tabs[idx + 1]);
                      }}
                      className="asseto-btn-secondary text-xs py-2 px-3.5 rounded-xl text-[#1758A2]"
                    >
                      <span>Next Tab</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  ) : null}

                  <button
                    type="submit"
                    disabled={modalSaving}
                    className="asseto-btn-primary text-xs py-2 px-5 rounded-xl"
                  >
                    {modalSaving ? 'Saving Changes...' : editMode ? 'Save All Details' : 'Create Student'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* DELETE CONFIRMATION MODAL */}
      {/* ========================================================================= */}
      {deleteConfirmOpen && studentToDelete && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in duration-150">
          <div className="bg-white border border-[#E8ECEF] rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-[#16283B]">Confirm Student Deletion</h3>
              <p className="text-xs text-[#64748B] mt-1">
                Are you sure you want to delete <span className="font-semibold text-[#16283B]">{studentToDelete.full_name}</span> ({studentToDelete.roll_no})?
                This action archives the record and safely removes access from active directories.
              </p>
            </div>
            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                onClick={() => setDeleteConfirmOpen(false)}
                className="asseto-btn-secondary text-xs py-2 px-4 rounded-xl"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteConfirm}
                disabled={deleting}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded-xl transition"
              >
                {deleting ? 'Deleting...' : 'Confirm Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* UPLOAD DOCUMENT MODAL (Passport Photo & Aadhaar) */}
      {/* ========================================================================= */}
      {docUploadOpen && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50 animate-in fade-in duration-150">
          <div className="bg-white border border-[#E8ECEF] rounded-2xl w-full max-w-md p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-[#16283B]">
                Upload {docType === 'photo' ? 'Passport Photograph' : 'Aadhaar Document'}
              </h3>
              <button onClick={() => setDocUploadOpen(false)} className="p-1 text-[#64748B]">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-[#64748B]">
              Target Roll Number: <span className="font-mono font-bold text-[#1758A2]">{docTargetRoll}</span>
            </p>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-[#16283B] mb-1">Document Type</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value as any)}
                  className="w-full py-2 px-3 text-xs bg-[#F6F6F6] border border-[#E8ECEF] rounded-xl"
                >
                  <option value="photo">Passport Photograph (JPG, PNG)</option>
                  <option value="aadhaar">Aadhaar Card (JPG, PNG)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-[#16283B] mb-1">Select File</label>
                <input
                  type="file"
                  required
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-[#64748B] file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-[#1758A2]/10 file:text-[#1758A2] hover:file:bg-[#1758A2]/20"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setDocUploadOpen(false)}
                  className="asseto-btn-secondary text-xs py-2 px-4 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading || !uploadFile}
                  className="asseto-btn-primary text-xs py-2 px-5 rounded-xl disabled:opacity-50"
                >
                  {uploading ? 'Uploading...' : 'Save Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
