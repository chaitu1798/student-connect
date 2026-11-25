export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'client';
  is_active: boolean;
  must_change_password: boolean;
  created_at?: string;
}

export interface Student {
  id?: number;
  // A. Basic Information
  s_no?: string | null;
  recorded_email?: string | null;
  roll_no: string;
  full_name: string;
  column1?: string | null;
  branch?: string | null;
  branch_code?: string | null;
  name_of_college?: string | null;
  college_name?: string | null;
  gender?: string | null;
  contact_no?: string | null;
  contact_number?: string | null;
  parent_contact_no?: string | null;
  parent_contact_number?: string | null;
  corrected_placements_email?: string | null;
  corrected_placement_email?: string | null;
  alternate_personal_email?: string | null;

  // B. UG / B.Tech Information
  ug_cgpa?: number | null;
  ug_year_of_pass?: number | null;
  ug_year_of_passing?: number | null;
  no_of_backlogs?: number | null;
  number_of_backlogs?: number | null;

  // C. Personal Information
  first_name?: string | null;
  middle_name?: string | null;
  last_name?: string | null;
  date_of_birth?: string | null;

  // D. CRT Information
  crt_registered?: string | null;

  // E. SSC / 10th Information
  x_grading_system?: string | null;
  x_cgpa_percentage?: string | null;
  x_year_of_pass?: number | null;
  x_year_of_passing?: number | null;
  x_school_name?: string | null;

  // F. Intermediate / Diploma Information
  study_after_x?: string | null;
  xii_grading_system?: string | null;
  xii_percentage_cgpa?: string | null;
  xii_cgpa_percentage?: string | null;
  xii_year_of_pass?: number | null;
  xii_year_of_passing?: number | null;
  xii_college_name?: string | null;

  // G. Admission Information
  admission_type?: string | null;
  entrance_exam?: string | null;
  entrance_rank?: string | null;

  // H. Family Information
  father_name?: string | null;
  father_occupation?: string | null;
  languages_known?: string | null;
  caste?: string | null;

  // I. Address and Identification
  residential_address?: string | null;
  full_residential_address?: string | null;
  pan_number?: string | null;
  aadhaar_number?: string | null;

  // J. Document Uploads
  aadhaar_image_path?: string | null;
  photo_image_path?: string | null;

  internship_count?: number;
  is_public_approved?: boolean;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface Internship {
  id?: string | number;
  s_no?: string | null;
  roll_no: string;
  student_id?: string | number | null;
  full_name?: string | null;
  branch?: string | null;
  college_name?: string | null;
  name_of_college?: string | null;
  organization_name: string;
  name_of_organization?: string | null;
  organization_district?: string | null;
  category?: string | null;
  role?: string | null;
  mode?: string | null;
  mode_of_internship?: string | null;
  internship_type?: string | null;
  stipend_amount?: number | null;
  stipend_range?: string | null;
  start_date?: string | null;
  end_date?: string | null;
  certificate_received?: string | null;
  duration_weeks?: number | null;
  organization_address?: string | null;
  offered_by?: string | null;
  internship_offered_by?: string | null;
  regular_internship?: string | null;
  gender?: string | null;
  contact_no?: string | null;
  contact_number?: string | null;
  certificate_path?: string | null;
  certificate_file_path?: string | null;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string | null;
}

export interface InternshipStats {
  total: number;
  total_organizations: number;
  branch_wise: { branch: string; count: number }[];
  organization_wise: { organization: string; count: number }[];
  district_wise: { district: string; count: number }[];
  certificate_status: {
    received: number;
    pending: number;
    received_percentage: number;
  };
  mode_wise: Record<string, number>;
  type_wise: Record<string, number>;
  stipend_stats: {
    paid_count: number;
    unpaid_count: number;
    avg_stipend: number;
    max_stipend: number;
    avg_duration_weeks: number;
  };
}

export interface PublicStudentProfile {
  full_name: string;
  roll_no: string;
  branch?: string | null;
  branch_code?: string | null;
  name_of_college?: string | null;
  college_name?: string | null;
  gender?: string | null;
  ug_cgpa?: number | null;
  ug_year_of_pass?: number | null;
  internship_count: number;
  photo_image_path?: string | null;
  internships: {
    organization_name: string;
    organization_district?: string | null;
    role?: string | null;
    category?: string | null;
    mode?: string | null;
    duration_weeks?: number | null;
    regular_internship?: string | null;
  }[];
}

export interface DashboardStats {
  total_students: number;
  total_internships: number;
  total_clients: number;
  total_admins?: number;
  total_reviewers?: number;
  total_branches: number;
  total_organizations?: number;

  // Student Stats
  completed_profiles?: number;
  incomplete_profiles?: number;
  branch_distribution: Record<string, number>;
  gender_distribution: Record<string, number>;
  admission_type_distribution?: Record<string, number>;

  // Internship Stats
  students_with_internships?: number;
  students_without_internships: number;
  organization_distribution: Record<string, number>;
  district_distribution?: Record<string, number>;
  category_distribution?: Record<string, number>;
  mode_distribution?: Record<string, number>;
  type_distribution?: Record<string, number>;
  stipend_range_distribution: Record<string, number>;
  certificates_received?: number;
  certificates_pending?: number;
  internships_by_branch?: Record<string, number>;

  // Academic Stats
  average_ug_cgpa?: number;
  avg_cgpa?: number;
  students_with_backlogs: number;
  students_without_backlogs?: number;
  year_distribution: Record<string, number>;
  crt_registered_count: number;
  crt_unregistered_count?: number;

  // System & Directory Stats
  approved_public_profiles?: number;
  pending_public_profiles?: number;
  recently_updated_students: {
    roll_no: string;
    full_name: string;
    branch: string;
    updated_at: string;
  }[];
  recent_internships?: {
    roll_no: string;
    full_name?: string;
    organization: string;
    role: string;
    updated_at: string;
  }[];
}

export interface PublicStats {
  total_students: number;
  total_internships: number;
  total_branches: number;
  branch_statistics: Record<string, number>;
  recent_approved_profiles: {
    roll_no: string;
    full_name: string;
    branch: string;
    branch_code?: string;
    ug_year_of_pass?: number;
    internship_count: number;
  }[];
  internship_highlights: {
    organization: string;
    count: number;
  }[];
}

export interface PublicPermission {
  id: number;
  student_id: number;
  roll_no: string;
  student_name: string;
  branch?: string;
  is_public_approved: boolean;
  publish_gender: boolean;
  publish_cgpa: boolean;
  publish_internships: boolean;
  student_consent_given: boolean;
}
