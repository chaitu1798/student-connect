from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.student import Student, StudentPublicationSetting, StudentAcademic
from app.models.document import StudentDocument
from app.models.internship import Internship
from app.schemas.student import PublicSearchResponse, PublicStudentSummary, PublicStudentDetail
from app.schemas.internship import InternshipOut

router = APIRouter(prefix="/public", tags=["Public Portal"])

@router.get("/search", response_model=PublicSearchResponse)
@router.get("/students/search", response_model=PublicSearchResponse)
def public_search_students(
    roll_number: str = Query(None, description="Exact or partial roll number"),
    full_name: str = Query(None, description="Partial full name"),
    branch: str = Query(None, description="Filter by branch"),
    q: str = Query(None, description="Unified search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search authorized student profiles. No login is required.
    Strictly filters for is_public_approved == True.
    """
    query = db.query(Student).join(
        StudentPublicationSetting, StudentPublicationSetting.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        StudentPublicationSetting.is_public_approved == True
    )

    if roll_number:
        query = query.filter(Student.roll_no.ilike(f"%{roll_number.strip()}%"))
    if full_name:
        query = query.filter(Student.full_name.ilike(f"%{full_name.strip()}%"))
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(or_(Student.roll_no.ilike(term), Student.full_name.ilike(term)))
    if branch:
        query = query.filter(Student.branch.ilike(f"%{branch.strip()}%"))

    total = query.count()
    offset = (page - 1) * page_size
    students = query.order_by(Student.roll_no.asc()).offset(offset).limit(page_size).all()

    items = []
    for s in students:
        i_cnt = db.query(func.count(Internship.id)).filter(
            Internship.roll_no == s.roll_no, Internship.is_deleted == False
        ).scalar() or 0
        yop = s.academics.ug_year_of_passing if s.academics else None
        photo_doc = db.query(StudentDocument).filter(
            StudentDocument.student_id == s.id,
            StudentDocument.document_type.in_(["PASSPORT_PHOTO", "PHOTO"])
        ).order_by(StudentDocument.created_at.desc()).first()
        photo_path = photo_doc.file_path if photo_doc else None
        items.append(PublicStudentSummary(
            roll_no=s.roll_no,
            full_name=s.full_name,
            branch=s.branch,
            branch_code=s.branch_code,
            ug_year_of_passing=yop,
            ug_year_of_pass=yop,
            internship_count=i_cnt,
            photo_image_path=photo_path,
        ))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

@router.get("/photo/{roll_number}")
def get_public_student_photo(roll_number: str, db: Session = Depends(get_db)):
    """Serves approved student photograph for public directory and profile cards."""
    import os
    from fastapi.responses import FileResponse
    from app.config import settings
    student = db.query(Student).filter(
        Student.roll_no.ilike(roll_number.strip()),
        Student.is_archived == False
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    photo_doc = db.query(StudentDocument).filter(
        StudentDocument.student_id == student.id,
        StudentDocument.document_type.in_(["PASSPORT_PHOTO", "PHOTO"])
    ).order_by(StudentDocument.created_at.desc()).first()
    
    if not photo_doc:
        raise HTTPException(status_code=404, detail="No photograph uploaded")
    clean_path = photo_doc.file_path.replace("\\", "/").strip("/ ")
    safe_path = os.path.normpath(os.path.join(settings.UPLOAD_DIR, clean_path))
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Photograph file missing")
    return FileResponse(safe_path, headers={"Cache-Control": "public, max-age=0, must-revalidate"})

@router.get("/profile/{roll_number}", response_model=PublicStudentDetail)
@router.get("/students/{roll_number}", response_model=PublicStudentDetail)
def get_public_student_profile(roll_number: str, db: Session = Depends(get_db)):
    """
    View authorized student profile & authorized internship history.
    Confidential data (Aadhaar, PAN, phone numbers, addresses, parent details, caste)
    is strictly never exposed.
    """
    student = db.query(Student).filter(
        Student.roll_no == roll_number,
        Student.is_archived == False
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    pub = student.publication_setting
    if not pub or not pub.is_public_approved:
        raise HTTPException(status_code=403, detail="Student profile is not authorized for public viewing")

    # Approved internships
    internships_list = []
    if pub.publish_internships:
        interns = db.query(Internship).filter(
            Internship.roll_no == student.roll_no,
            Internship.is_deleted == False
        ).all()
        for i in interns:
            internships_list.append({
                "organization_name": i.name_of_organization,
                "organization_district": i.organization_district,
                "role": i.role,
                "category": i.category,
                "mode": i.mode_of_internship,
                "duration_weeks": i.duration_weeks,
                "regular_internship": i.regular_internship,
            })

    # Academics
    ac = student.academics
    priv = student.private_data
    photo_doc = db.query(StudentDocument).filter(
        StudentDocument.student_id == student.id,
        StudentDocument.document_type.in_(["PASSPORT_PHOTO", "PHOTO"])
    ).order_by(StudentDocument.created_at.desc()).first()
    photo_path = photo_doc.file_path if photo_doc else None

    return PublicStudentDetail(
        full_name=student.full_name,
        roll_no=student.roll_no,
        branch=student.branch,
        branch_code=student.branch_code,
        gender=priv.gender if (priv and pub.publish_gender) else None,
        ug_cgpa=ac.ug_cgpa if (ac and pub.publish_cgpa) else None,
        ug_year_of_passing=ac.ug_year_of_passing if ac else None,
        ug_year_of_pass=ac.ug_year_of_passing if ac else None,
        internship_count=len(internships_list),
        internships=internships_list,
        photo_image_path=photo_path,
    )

@router.get("/internships", response_model=list[dict])
def get_public_internships(
    organization: str = Query(None),
    branch: str = Query(None),
    limit: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """View approved internship statistics and authorized history."""
    query = db.query(Internship).filter(Internship.is_deleted == False)
    if organization:
        query = query.filter(Internship.name_of_organization.ilike(f"%{organization}%"))
    if branch:
        query = query.filter(Internship.branch.ilike(f"%{branch}%"))

    items = query.order_by(Internship.id.desc()).limit(limit).all()
    return [
        {
            "id": i.id,
            "roll_no": i.roll_no,
            "full_name": i.full_name,
            "organization_name": i.name_of_organization,
            "organization_district": i.organization_district,
            "role": i.role,
            "category": i.category,
            "mode": i.mode_of_internship,
            "duration_weeks": i.duration_weeks,
        }
        for i in items
    ]

@router.get("/stats")
def get_public_stats(db: Session = Depends(get_db)):
    total_students = db.query(func.count(Student.id)).filter(Student.is_archived == False).scalar() or 0
    total_internships = db.query(func.count(Internship.id)).filter(Internship.is_deleted == False).scalar() or 0

    branch_rows = db.query(Student.branch, func.count(Student.id)).filter(
        Student.is_archived == False, Student.branch != None
    ).group_by(Student.branch).all()
    branch_stats = {b: cnt for b, cnt in branch_rows if b}

    top_orgs = db.query(Internship.name_of_organization, func.count(Internship.id)).filter(
        Internship.is_deleted == False
    ).group_by(Internship.name_of_organization).order_by(func.count(Internship.id).desc()).limit(6).all()

    highlights = [{"organization": org, "count": count} for org, count in top_orgs]

    recent_profiles = []
    approved = db.query(Student).join(
        StudentPublicationSetting, StudentPublicationSetting.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        StudentPublicationSetting.is_public_approved == True
    ).limit(6).all()

    for s in approved:
        i_cnt = db.query(func.count(Internship.id)).filter(
            Internship.roll_no == s.roll_no, Internship.is_deleted == False
        ).scalar() or 0
        yop = s.academics.ug_year_of_passing if s.academics else None
        recent_profiles.append({
            "roll_no": s.roll_no,
            "full_name": s.full_name,
            "branch": s.branch,
            "branch_code": s.branch_code,
            "ug_year_of_pass": yop,
            "internship_count": i_cnt,
        })

    return {
        "total_students": total_students,
        "total_internships": total_internships,
        "total_branches": len(branch_stats),
        "branch_statistics": branch_stats,
        "recent_approved_profiles": recent_profiles,
        "internship_highlights": highlights,
    }

@router.get("/suggestions")
def get_suggestions(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    term = f"%{q.strip()}%"
    results = db.query(Student.roll_no, Student.full_name, Student.branch).join(
        StudentPublicationSetting, StudentPublicationSetting.student_id == Student.id
    ).filter(
        Student.is_archived == False,
        StudentPublicationSetting.is_public_approved == True,
        or_(Student.roll_no.ilike(term), Student.full_name.ilike(term))
    ).limit(8).all()
    return [{"roll_no": r[0], "full_name": r[1], "branch": r[2]} for r in results]
