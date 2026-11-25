from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.student import (
    Student,
    StudentAcademic,
    StudentContact,
    StudentPrivateData,
    StudentPublicationSetting,
)
from app.models.internship import Internship
from app.models.organization import Organization, Branch
from app.routers.auth import require_role

router = APIRouter(tags=["Admin Analytics & Dashboard"])

def build_complete_analytics(db: Session) -> dict:
    # ---------------------------------------------------------
    # A. STUDENT STATISTICS
    # ---------------------------------------------------------
    total_students = db.query(func.count(Student.id)).filter(Student.is_archived == False).scalar() or 0

    branch_rows = db.query(Student.branch, func.count(Student.id)).filter(
        Student.is_archived == False, Student.branch != None
    ).group_by(Student.branch).all()
    branch_distribution = {b: cnt for b, cnt in branch_rows if b}

    gender_rows = db.query(StudentPrivateData.gender, func.count(Student.id)).join(
        StudentPrivateData, StudentPrivateData.student_id == Student.id
    ).filter(Student.is_archived == False).group_by(StudentPrivateData.gender).all()
    gender_distribution = {g if g else "Unspecified": cnt for g, cnt in gender_rows}

    adm_rows = db.query(StudentAcademic.admission_type, func.count(Student.id)).join(
        StudentAcademic, StudentAcademic.student_id == Student.id
    ).filter(Student.is_archived == False).group_by(StudentAcademic.admission_type).all()
    admission_type_distribution = {a if a else "General": cnt for a, cnt in adm_rows}

    completed_profiles = db.query(func.count(Student.id)).join(
        StudentAcademic, StudentAcademic.student_id == Student.id
    ).join(
        StudentContact, StudentContact.student_id == Student.id
    ).join(
        StudentPrivateData, StudentPrivateData.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        (StudentAcademic.ug_cgpa != None) | (StudentAcademic.ug_year_of_passing != None),
        (StudentContact.recorded_email != None) | (StudentContact.contact_number != None)
    ).scalar() or 0
    incomplete_profiles = max(0, total_students - completed_profiles)

    # ---------------------------------------------------------
    # B. INTERNSHIP STATISTICS
    # ---------------------------------------------------------
    total_internships = db.query(func.count(Internship.id)).filter(Internship.is_deleted == False).scalar() or 0

    students_with_internships = db.query(func.count(func.distinct(Internship.roll_no))).filter(
        Internship.is_deleted == False
    ).scalar() or 0
    students_without_internships = max(0, total_students - students_with_internships)

    org_rows = db.query(Internship.name_of_organization, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.name_of_organization != None
    ).group_by(Internship.name_of_organization).order_by(func.count(Internship.id).desc()).limit(15).all()
    organization_distribution = {org: cnt for org, cnt in org_rows if org}

    dist_rows = db.query(Internship.organization_district, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.organization_district != None
    ).group_by(Internship.organization_district).order_by(func.count(Internship.id).desc()).limit(15).all()
    district_distribution = {d: cnt for d, cnt in dist_rows if d}

    cat_rows = db.query(Internship.category, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.category != None
    ).group_by(Internship.category).all()
    category_distribution = {c: cnt for c, cnt in cat_rows if c}

    mode_rows = db.query(Internship.mode_of_internship, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.mode_of_internship != None
    ).group_by(Internship.mode_of_internship).all()
    mode_distribution = {m: cnt for m, cnt in mode_rows if m}

    type_rows = db.query(Internship.internship_type, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.internship_type != None
    ).group_by(Internship.internship_type).all()
    type_distribution = {t: cnt for t, cnt in type_rows if t}

    stipend_rows = db.query(Internship.stipend_range, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.stipend_range != None
    ).group_by(Internship.stipend_range).all()
    stipend_range_distribution = {s: cnt for s, cnt in stipend_rows if s}

    cert_rcvd = db.query(func.count(Internship.id)).filter(
        Internship.is_deleted == False,
        func.lower(Internship.certificate_received) == "yes"
    ).scalar() or 0
    cert_pending = max(0, total_internships - cert_rcvd)

    branch_int_rows = db.query(Internship.branch, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.branch != None
    ).group_by(Internship.branch).order_by(func.count(Internship.id).desc()).all()
    internships_by_branch = {b: cnt for b, cnt in branch_int_rows if b}

    # ---------------------------------------------------------
    # C. ACADEMIC STATISTICS
    # ---------------------------------------------------------
    avg_cgpa_row = db.query(func.avg(StudentAcademic.ug_cgpa)).join(
        Student, Student.id == StudentAcademic.student_id
    ).filter(
        Student.is_archived == False,
        StudentAcademic.ug_cgpa != None,
        StudentAcademic.ug_cgpa > 0
    ).scalar()
    average_ug_cgpa = round(float(avg_cgpa_row), 2) if avg_cgpa_row else 0.0

    students_with_backlogs = db.query(func.count(Student.id)).join(
        StudentAcademic, StudentAcademic.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        StudentAcademic.number_of_backlogs > 0
    ).scalar() or 0
    students_without_backlogs = max(0, total_students - students_with_backlogs)

    yop_rows = db.query(StudentAcademic.ug_year_of_passing, func.count(Student.id)).join(
        StudentAcademic, StudentAcademic.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        StudentAcademic.ug_year_of_passing != None
    ).group_by(StudentAcademic.ug_year_of_passing).order_by(StudentAcademic.ug_year_of_passing.asc()).all()
    year_distribution = {str(y): cnt for y, cnt in yop_rows if y}

    crt_registered_count = db.query(func.count(Student.id)).join(
        StudentAcademic, StudentAcademic.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        func.upper(StudentAcademic.crt_registered) == "Y"
    ).scalar() or 0
    crt_unregistered_count = max(0, total_students - crt_registered_count)

    # ---------------------------------------------------------
    # D. SYSTEM & ADMINISTRATIVE STATISTICS
    # ---------------------------------------------------------
    total_admins = db.query(func.count(User.id)).filter(
        func.upper(User.role).in_(["ADMIN", "SUPER_ADMIN"])
    ).scalar() or 0
    total_clients = db.query(func.count(User.id)).filter(
        func.upper(User.role) == "CLIENT"
    ).scalar() or 0
    total_reviewers = db.query(func.count(User.id)).filter(
        func.upper(User.role) == "REVIEWER"
    ).scalar() or 0

    approved_public_profiles = db.query(func.count(StudentPublicationSetting.id)).join(
        Student, Student.id == StudentPublicationSetting.student_id
    ).filter(
        Student.is_archived == False,
        StudentPublicationSetting.is_public_approved == True
    ).scalar() or 0
    pending_public_profiles = max(0, total_students - approved_public_profiles)

    # Recently registered / updated students
    recent_stus = db.query(Student).filter(
        Student.is_archived == False
    ).order_by(Student.updated_at.desc()).limit(6).all()
    recently_updated_students = [
        {
            "roll_no": st.roll_no,
            "full_name": st.full_name,
            "branch": st.branch or "General",
            "updated_at": st.updated_at.isoformat() if st.updated_at else datetime.now(timezone.utc).isoformat()
        }
        for st in recent_stus
    ]

    # Recent internship updates
    recent_ints = db.query(Internship).filter(
        Internship.is_deleted == False
    ).order_by(Internship.updated_at.desc()).limit(6).all()
    recent_internships = [
        {
            "roll_no": it.roll_no,
            "full_name": it.full_name or "Student",
            "organization": it.name_of_organization,
            "role": it.role or "Intern",
            "updated_at": it.updated_at.isoformat() if it.updated_at else datetime.now(timezone.utc).isoformat()
        }
        for it in recent_ints
    ]

    total_organizations = len(organization_distribution) or db.query(func.count(Organization.id)).scalar() or 0
    total_branches = len(branch_distribution) or db.query(func.count(Branch.id)).scalar() or 0

    return {
        # High-level counters
        "total_students": total_students,
        "total_internships": total_internships,
        "total_branches": total_branches,
        "total_organizations": total_organizations,
        "total_clients": total_clients,
        "total_admins": total_admins,
        "total_reviewers": total_reviewers,

        # Category A: Student Stats
        "branch_distribution": branch_distribution,
        "gender_distribution": gender_distribution,
        "admission_type_distribution": admission_type_distribution,
        "completed_profiles": completed_profiles,
        "incomplete_profiles": incomplete_profiles,

        # Category B: Internship Stats
        "students_with_internships": students_with_internships,
        "students_without_internships": students_without_internships,
        "organization_distribution": organization_distribution,
        "district_distribution": district_distribution,
        "category_distribution": category_distribution,
        "mode_distribution": mode_distribution,
        "type_distribution": type_distribution,
        "stipend_range_distribution": stipend_range_distribution,
        "certificates_received": cert_rcvd,
        "certificates_pending": cert_pending,
        "internships_by_branch": internships_by_branch,

        # Category C: Academic Stats
        "average_ug_cgpa": average_ug_cgpa,
        "avg_cgpa": average_ug_cgpa,
        "students_with_backlogs": students_with_backlogs,
        "students_without_backlogs": students_without_backlogs,
        "year_distribution": year_distribution,
        "crt_registered_count": crt_registered_count,
        "crt_unregistered_count": crt_unregistered_count,

        # Category D: System & Audit Stats
        "approved_public_profiles": approved_public_profiles,
        "pending_public_profiles": pending_public_profiles,
        "recently_updated_students": recently_updated_students,
        "recent_internships": recent_internships,
    }

@router.get("/dashboard-stats")
@router.get("/admin/dashboard-stats")
@router.get("/overview")
@router.get("/admin/analytics/overview")
def get_dashboard_statistics(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    return build_complete_analytics(db)

@router.get("/branches")
@router.get("/admin/analytics/branches")
def get_branch_analytics(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    rows = db.query(Student.branch, func.count(Student.id)).filter(
        Student.is_archived == False, Student.branch != None
    ).group_by(Student.branch).all()
    return [{"branch": b, "count": cnt} for b, cnt in rows if b]

@router.get("/internships")
@router.get("/admin/analytics/internships")
def get_internship_analytics(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    by_category = db.query(Internship.category, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.category != None
    ).group_by(Internship.category).all()

    by_mode = db.query(Internship.mode_of_internship, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.mode_of_internship != None
    ).group_by(Internship.mode_of_internship).all()

    by_type = db.query(Internship.internship_type, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.internship_type != None
    ).group_by(Internship.internship_type).all()

    return {
        "by_category": [{"category": c, "count": cnt} for c, cnt in by_category],
        "by_mode": [{"mode": m, "count": cnt} for m, cnt in by_mode],
        "by_type": [{"type": t, "count": cnt} for t, cnt in by_type],
    }

@router.get("/organizations")
@router.get("/admin/analytics/organizations")
def get_organization_analytics(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    top_orgs = db.query(Internship.name_of_organization, func.count(Internship.id)).filter(
        Internship.is_deleted == False, Internship.name_of_organization != None
    ).group_by(Internship.name_of_organization).order_by(func.count(Internship.id).desc()).limit(15).all()

    return [{"organization": org, "internship_count": cnt} for org, cnt in top_orgs]
