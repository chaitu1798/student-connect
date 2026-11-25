# STUDENT INFORMATION & INTERNSHIP MANAGEMENT SYSTEM

A production-ready enterprise web application engineered for educational institutions to maintain student academic records, personal information, placement credentials, internship records, and uploaded documents.

---

## 🏛️ Key System Interfaces

1. **Public Student Search Website**:
   - Modern university portal with institution branding, live database statistics, branch-wise metrics, and corporate internship highlights.
   - Prominent search bar supporting exact Roll Number, partial Name, case-insensitive query, and real-time suggestion dropdown.
   - Verified public student profile strictly showing approved academic information (Name, Roll No, Branch, Branch Code, Gender if approved, CGPA if approved, Year of Pass, approved internship details).
   - Confidential identification data (Aadhaar, PAN, phone numbers, addresses, parent details, caste, uploaded ID documents) is never exposed publicly.
   - Public Student Directory and Corporate Internship Directory with server-side filters and pagination.

2. **Client Portal (Faculty & Placement Officers)**:
   - Live analytics dashboard (Total Students, Total Internships, Branches, Students with Backlogs, CRT Registered, Students without Internships, Recently Updated Records).
   - Complete 41-field Student Information Module organized in 7 intuitive tabbed sections.
   - Complete 22-field Internship Management Module with auto-calculated inclusive duration in weeks and certificate upload/download.
   - **Document Upload & Staged Import Engine**:
     - Supports `.xlsx`, `.xls`, `.csv`, and digital/scanned `.pdf` documents for both Student and Internship schemas.
     - **Zero-Direct-Overwrite Policy**: All client document uploads are staged into isolated staging tables (`import_jobs`, `import_rows`, `import_changes`).
     - Automated header synonym matching, duplicate detection, and Old vs. New value diff generation.
     - Interactive preview showing detected records and field-level diffs.
     - Submission to Administrator review queue for approval or rejection.
   - Dedicated PDF Data Extraction interface with PyPDF and OCR extraction, student roll number matching, and interactive review before database commit.
   - Report generator with Excel, CSV, and PDF export across 8 report categories.

3. **Administrator Dashboard & Governance Portal**:
   - **Import Approvals Engine**: Inspect submitted client import jobs, review old vs. proposed value diffs, and execute atomic, transactional database commits upon approval or provide feedback on rejection.
   - Client account management (create client, activate/deactivate, reset passwords).
   - Public profile approval and granular privacy visibility controls (toggle public approval, toggle publish gender, toggle publish CGPA, toggle publish internships).
   - Complete system audit logging of all actions (`CREATE`, `UPDATE`, `DELETE`, `IMPORT`, `APPROVE_IMPORT`, `REJECT_IMPORT`, `EXPORT`, `APPROVE_PROFILE`, `LOGIN`).
   - Default administrator credentials (`admin` / `ChangeMe123!`) with mandatory password change enforcement on initial login.

---

## 💻 Technology Stack

- **Frontend**:
  - React 19, TypeScript
  - Tailwind CSS v4, PostCSS
  - Lucide React icons
  - Axios with JWT token interceptors and auto-redirects
  - Vite development server & production bundler

- **Backend**:
  - Python FastAPI (REST APIs, OpenAPI / Swagger documentation at `/api/docs`)
  - JWT Authentication (HS256) with access tokens & secure refresh sessions
  - Role-Based Access Control (`SUPER_ADMIN`, `ADMIN`, `REVIEWER`, `CLIENT`, `PUBLIC`)
  - SQLAlchemy 2.0 ORM with relationship safety and soft deletion

- **Database Architecture**:
  - Normalized schema with UUID primary keys across 22 core tables:
    `students`, `branches`, `colleges`, `student_contacts`, `student_academics`, `student_private_data`, `student_documents`, `student_addresses`, `student_consents`, `student_publication_settings`, `internships`, `organizations`, `users`, `client_organizations`, `import_jobs`, `import_rows`, `import_changes`, `import_column_mappings`, `approval_actions`, `audit_logs`, `refresh_sessions`, `system_settings`.
  - SQLite default (zero-configuration development and evaluation)
  - PostgreSQL supported via `DATABASE_URL` environment variable

- **File & Data Processing**:
  - Pandas & OpenPyXL for Excel / CSV processing
  - PyPDF & Pytesseract for PDF text and OCR extraction
  - Pillow for image handling
  - ReportLab for PDF report generation

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node.js v24)

### 1. One-Click Batch Launchers (Windows)

- Double click `start_backend.bat` to launch the FastAPI backend server on `http://127.0.0.1:8000`.
- Double click `start_frontend.bat` to launch the Vite + React frontend portal on `http://localhost:5173`.

### 2. Manual Terminal Launch

**Backend Server:**
```bash
cd "d:\Student details portal"
.\venv\Scripts\activate
uvicorn app.main:app --app-dir backend --reload --port 8000
```
- API Base URL: `http://127.0.0.1:8000/api/v1`
- Interactive OpenAPI / Swagger Documentation: `http://127.0.0.1:8000/api/docs`

**Frontend Portal:**
```bash
cd "d:\Student details portal\frontend"
npm run dev
```
- Web Application: `http://localhost:5173`

---

## 🔑 Default Initial Credentials

| Role | Username | Initial Password | Notes |
|---|---|---|---|
| **Administrator** | `admin` | `ChangeMe123!` | Prompted to change password on first login |
| **Client / Faculty** | `client` | `Client123!` | Client portal access with staged import workflow |
| **Reviewer** | `reviewer` | `Reviewer123!` | Staged import review and approvals |

---

## 📊 Modules & Features

### 1. Student Information Module (All 41 Fields)
Organized in 7 tabs:
1. **Basic Info**: S.No., Email Address (Recorded), Roll No. (Unique), Full Name (As per SSC), Column1 (Legacy Preserved), Branch, Branch Code, Gender, Contact No., Parent Contact No., Corrected Placements Email ID, Alternate Personal Email ID.
2. **UG / B.Tech**: UG/B.Tech CGPA, UG Year of Pass, No. of Backlogs.
3. **Personal**: First Name, Middle Name, Last Name, Date of Birth.
4. **CRT**: CRT Registered (Y/N).
5. **SSC / 10th**: Xth Grading System, Enter Xth CGPA/Percentage, Grade X Year of Pass, Name of the School.
6. **Intermediate / Diploma**: Study after Xth, XIIth/Diploma Grading System, Enter XIIth/Diploma Percentage/CGPA, Grade XIIth/Diploma Year of Pass, XIIth/Diploma College Name.
7. **Admission, Family & ID**: Admission Type, Entrance Exam, Rank, Father Name, Father Occupation, Languages Known, Caste, Full Residential Address, PAN Card Number, Aadhaar Number.
8. **Document Uploads**: Upload Aadhaar Card (Image) and Latest Passport Size Photograph.

### 2. Internship Management Module (All 22 Fields)
- Attributes: S.No., Roll No., Full Name, Branch, Name of College, Name of Organization, Organization District, Category, Role, Mode (Online/Offline/Hybrid), Internship Type (Paid/Unpaid), Monthly Stipend (₹), Start Date, End Date, Certificate Received (Yes/No), Duration in Weeks (**automatically computed using inclusive date logic** `(end_date - start_date).days + 1`), Organization Address, Stipend Range, Offered By, Regular Internship (AEP / IDEA LAB), Gender, Contact No.
- Certificate upload (PDF / JPG / PNG) and authenticated download.
- Full CRUD operations with multiple internships supported per student.

### 3. Document Staged Import & Approval Workflow
- Dedicated upload interface for `.xlsx`, `.xls`, `.csv`, and `.pdf`.
- Template 1: Student Information Schema (41 fields).
- Template 2: Internship Information Schema (22 fields).
- Staged ingestion with `POST /api/v1/client/imports`:
  1. Upload document & verify file signature/mime-type.
  2. Parse and normalize headers via synonym dictionary.
  3. Detect duplicates and match against existing Roll Numbers.
  4. Compare with master records and generate field-level diffs (`old_value` vs `new_value`).
  5. Interactive review and client submission (`POST /api/v1/client/imports/{id}/submit`).
  6. Administrator inspects diffs (`GET /api/v1/admin/imports/{id}/diff`).
  7. Administrator approves (`POST /api/v1/admin/imports/{id}/approve`) or rejects (`POST /api/v1/admin/imports/{id}/reject`) with remarks.
  8. Approved changes are applied atomically inside a single database transaction.

### 4. PDF Data Extraction & OCR
- Upload application PDFs, transcripts, or certificates.
- Automated extraction of readable text (PyPDF) and scanned image text (OCR).
- Heuristic parsing for Roll Number, Candidate Name, Branch, CGPA, Contact, Email.
- Matches extracted Roll No with existing student database.
- Interactive review before database commit.

### 5. Reports & Exports
Generates reports in Excel (`.xlsx`), CSV (`.csv`), and PDF formats:
- Complete student Excel report
- Student-wise academic report
- Comprehensive internship report
- Organization-wise internship report
- CRT registration report
- Backlog standing report
- Students without internships
- Internship certificate pending report

---

## 🧪 Automated Testing

Run the full backend test suite with `pytest`:
```bash
.\venv\Scripts\pytest backend\tests\test_backend.py -v
```

All 7 core test suites verify:
- System health and database connectivity
- JWT authentication, session refresh, and mandatory password reset workflows
- Public student search with case-insensitivity, partial matching, and privacy shielding
- Public internship directory queries
- Full Administrator Student CRUD and archiving
- End-to-end staged import, diff generation, client submission, and administrator approval
- Administrator analytics overview across branches, backlogs, and placements

---

## 🐳 Docker Deployment

To launch the full stack with Docker Compose:
```bash
docker-compose up --build
```
- Frontend will run on port `3000`
- Backend will run on port `8000`
