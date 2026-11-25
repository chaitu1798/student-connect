from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.user import User
from app.models.student import (
    Student,
    StudentContact,
    StudentAcademic,
    StudentPrivateData,
    StudentAddress,
    StudentConsent,
    StudentPublicationSetting,
)
from app.models.document import StudentDocument
from app.models.internship import Internship
from app.schemas.student import StudentCreate, StudentPatch, StudentOut, StudentListResponse
from app.routers.auth import require_role
from app.services.audit_service import log_audit
from app.utils.security import mask_aadhaar, mask_pan

router = APIRouter(tags=["Student Management"])

def build_student_out(s: Student, db: Session, mask_sensitive: bool = False) -> StudentOut:
    i_cnt = db.query(func.count(Internship.id)).filter(
        Internship.roll_no == s.roll_no, Internship.is_deleted == False
    ).scalar() or 0

    pub = s.publication_setting
    ac = s.academics
    ct = s.contacts
    priv = s.private_data
    addr = s.addresses

    # Check for latest uploaded documents
    photo_doc = db.query(StudentDocument).filter(
        StudentDocument.student_id == s.id,
        StudentDocument.document_type.in_(["PASSPORT_PHOTO", "PHOTO"])
    ).order_by(StudentDocument.created_at.desc()).first()

    aadhaar_doc = db.query(StudentDocument).filter(
        StudentDocument.student_id == s.id,
        StudentDocument.document_type == "AADHAAR"
    ).order_by(StudentDocument.created_at.desc()).first()

    photo_path = photo_doc.file_path if photo_doc else None
    aadhaar_path = aadhaar_doc.file_path if aadhaar_doc else None

    # Handle masked sensitive values
    pan_val = priv.pan_number if priv else None
    aadhaar_val = priv.aadhaar_number if priv else None
    if mask_sensitive:
        pan_val = mask_pan(pan_val)
        aadhaar_val = mask_aadhaar(aadhaar_val)

    return StudentOut(
        id=s.id,
        s_no=s.s_no,
        roll_no=s.roll_no,
        full_name=s.full_name,
        first_name=s.first_name,
        middle_name=s.middle_name,
        last_name=s.last_name,
        branch=s.branch,
        branch_code=s.branch_code,
        name_of_college=s.name_of_college,
        column1=s.column1,

        recorded_email=ct.recorded_email if ct else None,
        corrected_placement_email=ct.corrected_placement_email if ct else None,
        alternate_personal_email=ct.alternate_personal_email if ct else None,
        contact_number=ct.contact_number if ct else None,
        parent_contact_number=ct.parent_contact_number if ct else None,

        ug_cgpa=ac.ug_cgpa if ac else None,
        ug_year_of_passing=ac.ug_year_of_passing if ac else None,
        number_of_backlogs=ac.number_of_backlogs if ac else 0,
        crt_registered=ac.crt_registered if ac else "N",
        x_grading_system=ac.x_grading_system if ac else None,
        x_cgpa_percentage=ac.x_cgpa_percentage if ac else None,
        x_year_of_passing=ac.x_year_of_passing if ac else None,
        x_school_name=ac.x_school_name if ac else None,
        study_after_x=ac.study_after_x if ac else None,
        xii_grading_system=ac.xii_grading_system if ac else None,
        xii_cgpa_percentage=ac.xii_cgpa_percentage if ac else None,
        xii_year_of_passing=ac.xii_year_of_passing if ac else None,
        xii_college_name=ac.xii_college_name if ac else None,
        admission_type=ac.admission_type if ac else None,
        entrance_exam=ac.entrance_exam if ac else None,
        entrance_rank=ac.entrance_rank if ac else None,

        gender=priv.gender if priv else None,
        date_of_birth=priv.date_of_birth if priv else None,
        languages_known=priv.languages_known if priv else None,
        father_name=priv.father_name if priv else None,
        father_occupation=priv.father_occupation if priv else None,
        caste=priv.caste if priv else None,
        pan_number=pan_val,
        aadhaar_number=aadhaar_val,

        full_residential_address=addr.full_residential_address if addr else None,
        is_archived=s.is_archived,
        internship_count=i_cnt,
        is_public_approved=pub.is_public_approved if pub else False,
        created_at=s.created_at,
        updated_at=s.updated_at,

        photo_image_path=photo_path,
        aadhaar_image_path=aadhaar_path,

        # Synonyms for frontend convenience
        contact_no=ct.contact_number if ct else None,
        parent_contact_no=ct.parent_contact_number if ct else None,
        corrected_placements_email=ct.corrected_placement_email if ct else None,
        ug_year_of_pass=ac.ug_year_of_passing if ac else None,
        no_of_backlogs=ac.number_of_backlogs if ac else 0,
        residential_address=addr.full_residential_address if addr else None,
        x_year_of_pass=ac.x_year_of_passing if ac else None,
        xii_percentage_cgpa=ac.xii_cgpa_percentage if ac else None,
        xii_year_of_pass=ac.xii_year_of_passing if ac else None,
    )

# --- List Students (Supports both /students and /admin/students) ---
@router.get("/students", response_model=StudentListResponse)
@router.get("/admin/students", response_model=StudentListResponse)
def list_students(
    search: str = Query("", description="Roll No or Name"),
    branch: str = Query(None),
    year: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    query = db.query(Student).filter(Student.is_archived == False)

    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(Student.roll_no.ilike(term), Student.full_name.ilike(term)))
    if branch:
        query = query.filter(Student.branch.ilike(f"%{branch}%"))
    if year:
        query = query.join(StudentAcademic, StudentAcademic.student_id == Student.id).filter(
            StudentAcademic.ug_year_of_passing == year
        )

    total = query.count()
    offset = (page - 1) * page_size
    students = query.order_by(Student.roll_no.asc()).offset(offset).limit(page_size).all()

    mask_sens = current_user.role not in ["SUPER_ADMIN", "ADMIN"]
    items = [build_student_out(s, db, mask_sens) for s in students]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

# --- Create / Register New Student (Supports both /students and /admin/students) ---
@router.post("/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
@router.post("/admin/students", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    data: StudentCreate,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "CLIENT", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    existing = db.query(Student).filter(Student.roll_no == data.roll_no).first()
    if existing:
        if existing.is_archived:
            existing.is_archived = False
            db.commit()
            return build_student_out(existing, db)
        raise HTTPException(status_code=400, detail=f"Student with Roll No {data.roll_no} already exists")

    student = Student(
        s_no=data.s_no,
        roll_no=data.roll_no,
        full_name=data.full_name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        last_name=data.last_name,
        branch=data.branch,
        branch_code=data.branch_code,
        name_of_college=data.name_of_college,
        column1=data.column1,
        created_by_user_id=current_user.id,
    )
    db.add(student)
    db.flush()

    contacts = StudentContact(
        student_id=student.id,
        recorded_email=data.recorded_email,
        corrected_placement_email=data.corrected_placement_email,
        alternate_personal_email=data.alternate_personal_email,
        contact_number=data.contact_number,
        parent_contact_number=data.parent_contact_number,
    )
    db.add(contacts)

    academics = StudentAcademic(
        student_id=student.id,
        ug_cgpa=data.ug_cgpa,
        ug_year_of_passing=data.ug_year_of_passing,
        number_of_backlogs=data.number_of_backlogs or 0,
        crt_registered=data.crt_registered or "N",
        x_grading_system=data.x_grading_system,
        x_cgpa_percentage=data.x_cgpa_percentage,
        x_year_of_passing=data.x_year_of_passing,
        x_school_name=data.x_school_name,
        study_after_x=data.study_after_x,
        xii_grading_system=data.xii_grading_system,
        xii_cgpa_percentage=data.xii_cgpa_percentage,
        xii_year_of_passing=data.xii_year_of_passing,
        xii_college_name=data.xii_college_name,
        admission_type=data.admission_type,
        entrance_exam=data.entrance_exam,
        entrance_rank=data.entrance_rank,
    )
    db.add(academics)

    private_data = StudentPrivateData(
        student_id=student.id,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        languages_known=data.languages_known,
        father_name=data.father_name,
        father_occupation=data.father_occupation,
        caste=data.caste,
        pan_number=data.pan_number,
        aadhaar_number=data.aadhaar_number,
    )
    db.add(private_data)

    address = StudentAddress(
        student_id=student.id,
        full_residential_address=data.full_residential_address,
    )
    db.add(address)

    pub = StudentPublicationSetting(
        student_id=student.id,
        is_public_approved=False,
        publish_gender=False,
        publish_cgpa=False,
        publish_internships=True,
    )
    db.add(pub)

    consent = StudentConsent(student_id=student.id, consent_given=True)
    db.add(consent)

    if data.photo_image_path:
        db.add(StudentDocument(
            student_id=student.id,
            roll_no=student.roll_no,
            document_type="PASSPORT_PHOTO",
            original_filename="photo.jpg",
            file_path=data.photo_image_path,
            uploaded_by_user_id=current_user.id,
        ))

    if data.aadhaar_image_path:
        db.add(StudentDocument(
            student_id=student.id,
            roll_no=student.roll_no,
            document_type="AADHAAR",
            original_filename="aadhaar.jpg",
            file_path=data.aadhaar_image_path,
            uploaded_by_user_id=current_user.id,
        ))

    db.commit()
    log_audit(db, current_user.id, current_user.username, "CREATE", "student", student.id, f"Created student {student.full_name} ({student.roll_no})")
    return build_student_out(student, db)

# --- Get Student Details (Supports both /students/{id} and /admin/students/{id}) ---
@router.get("/students/{id}", response_model=StudentOut)
@router.get("/admin/students/{id}", response_model=StudentOut)
def get_student(
    id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        or_(Student.id == id, Student.roll_no == id),
        Student.is_archived == False
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student record not found")

    mask_sens = current_user.role not in ["SUPER_ADMIN", "ADMIN"]
    return build_student_out(student, db, mask_sens)

# --- Update Student Details (Supports PUT & PATCH on both paths) ---
@router.put("/students/{id}", response_model=StudentOut)
@router.patch("/students/{id}", response_model=StudentOut)
@router.put("/admin/students/{id}", response_model=StudentOut)
@router.patch("/admin/students/{id}", response_model=StudentOut)
def update_or_patch_student(
    id: str,
    patch_in: StudentPatch,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "CLIENT", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(
        or_(Student.id == id, Student.roll_no == id),
        Student.is_archived == False
    ).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    p = patch_in.model_dump(exclude_unset=True)

    # Main student attributes
    for f in ["s_no", "full_name", "first_name", "middle_name", "last_name", "branch", "branch_code", "name_of_college", "column1"]:
        if f in p and p[f] is not None:
            setattr(student, f, p[f])

    # Academics
    if not student.academics:
        student.academics = StudentAcademic(student_id=student.id)
        db.add(student.academics)
    for f in [
        "ug_cgpa", "ug_year_of_passing", "number_of_backlogs", "crt_registered",
        "x_grading_system", "x_cgpa_percentage", "x_year_of_passing", "x_school_name",
        "study_after_x", "xii_grading_system", "xii_cgpa_percentage", "xii_year_of_passing",
        "xii_college_name", "admission_type", "entrance_exam", "entrance_rank"
    ]:
        if f in p and p[f] is not None:
            setattr(student.academics, f, p[f])

    # Contacts
    if not student.contacts:
        student.contacts = StudentContact(student_id=student.id)
        db.add(student.contacts)
    for f in ["contact_number", "parent_contact_number", "recorded_email", "corrected_placement_email", "alternate_personal_email"]:
        if f in p and p[f] is not None:
            setattr(student.contacts, f, p[f])

    # Private data
    if not student.private_data:
        student.private_data = StudentPrivateData(student_id=student.id)
        db.add(student.private_data)
    for f in ["gender", "date_of_birth", "languages_known", "father_name", "father_occupation", "caste", "pan_number", "aadhaar_number"]:
        if f in p and p[f] is not None:
            setattr(student.private_data, f, p[f])

    # Address
    if not student.addresses:
        student.addresses = StudentAddress(student_id=student.id)
        db.add(student.addresses)
    if "full_residential_address" in p and p["full_residential_address"] is not None:
        student.addresses.full_residential_address = p["full_residential_address"]

    student.updated_by_user_id = current_user.id
    db.commit()

    log_audit(db, current_user.id, current_user.username, "UPDATE", "student", student.id, f"Updated student {student.roll_no}")
    return build_student_out(student, db)

# --- Delete / Archive Student ---
@router.delete("/students/{id}")
@router.delete("/admin/students/{id}")
@router.post("/admin/students/{id}/archive")
def archive_or_delete_student(
    id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(or_(Student.id == id, Student.roll_no == id)).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_archived = True
    student.updated_by_user_id = current_user.id
    db.commit()

    log_audit(db, current_user.id, current_user.username, "ARCHIVE", "student", student.id, f"Archived student {student.roll_no}")
    return {"message": f"Student {student.roll_no} deleted successfully (archived)"}
