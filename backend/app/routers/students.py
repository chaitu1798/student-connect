from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.internship import Internship
from app.models.permissions import PublicProfilePermission
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut, StudentListResponse
from app.routers.auth import get_current_user, require_role
from app.services.audit_service import log_audit
from app.utils.security import mask_aadhaar, mask_pan

router = APIRouter(prefix="/students", tags=["Student Management"])

@router.get("", response_model=StudentListResponse)
def list_students(
    search: str = Query("", description="Search by Roll No or Name"),
    branch: str = Query(None),
    gender: str = Query(None),
    year: int = Query(None),
    crt: str = Query(None),
    has_backlogs: bool = Query(None),
    min_cgpa: float = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Student).filter(Student.is_deleted == False)

    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(Student.roll_no.ilike(term), Student.full_name.ilike(term)))

    if branch:
        query = query.filter(Student.branch.ilike(f"%{branch}%"))
    if gender:
        query = query.filter(Student.gender == gender)
    if year:
        query = query.filter(Student.ug_year_of_pass == year)
    if crt:
        query = query.filter(Student.crt_registered == crt)
    if has_backlogs is True:
        query = query.filter(Student.no_of_backlogs > 0)
    elif has_backlogs is False:
        query = query.filter(or_(Student.no_of_backlogs == 0, Student.no_of_backlogs == None))
    if min_cgpa is not None:
        query = query.filter(Student.ug_cgpa >= min_cgpa)

    total = query.count()
    offset = (page - 1) * page_size
    students = query.order_by(Student.roll_no.asc()).offset(offset).limit(page_size).all()

    items = []
    for s in students:
        i_cnt = db.query(func.count(Internship.id)).filter(
            Internship.roll_no == s.roll_no, Internship.is_deleted == False
        ).scalar() or 0
        perm = db.query(PublicProfilePermission).filter(PublicProfilePermission.student_id == s.id).first()
        
        # Build student output
        s_dict = {c.name: getattr(s, c.name) for c in s.__table__.columns}
        # Mask sensitive identification for safety unless requested by authorized edit
        if current_user.role != "admin":
            s_dict["aadhaar_number"] = mask_aadhaar(s.aadhaar_number)
            s_dict["pan_number"] = mask_pan(s.pan_number)
        s_dict["internship_count"] = i_cnt
        s_dict["is_public_approved"] = perm.is_public_approved if perm else False
        items.append(StudentOut(**s_dict))

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

@router.get("/{roll_no}", response_model=StudentOut)
def get_student(
    roll_no: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == roll_no, Student.is_deleted == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    i_cnt = db.query(func.count(Internship.id)).filter(
        Internship.roll_no == student.roll_no, Internship.is_deleted == False
    ).scalar() or 0
    perm = db.query(PublicProfilePermission).filter(PublicProfilePermission.student_id == student.id).first()

    s_dict = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    s_dict["internship_count"] = i_cnt
    s_dict["is_public_approved"] = perm.is_public_approved if perm else False
    return StudentOut(**s_dict)

@router.post("", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(
    student_in: StudentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(Student).filter(Student.roll_no == student_in.roll_no).first()
    if existing:
        if not existing.is_deleted:
            raise HTTPException(status_code=400, detail=f"Student with Roll No {student_in.roll_no} already exists")
        else:
            # Revive soft-deleted student
            existing.is_deleted = False
            for k, v in student_in.model_dump(exclude_unset=True).items():
                setattr(existing, k, v)
            existing.updated_by_user_id = current_user.id
            db.commit()
            log_audit(db, current_user.id, current_user.username, "RESTORE", "student", existing.roll_no)
            return existing

    new_student = Student(
        **student_in.model_dump(),
        created_by_user_id=current_user.id,
    )
    db.add(new_student)
    db.flush()

    # Create or update public profile permission record
    perm = db.query(PublicProfilePermission).filter(
        (PublicProfilePermission.student_id == new_student.id) | (PublicProfilePermission.roll_no == new_student.roll_no)
    ).first()
    if not perm:
        perm = PublicProfilePermission(
            student_id=new_student.id,
            roll_no=new_student.roll_no,
            is_public_approved=False,
            publish_gender=False,
            publish_cgpa=False,
            publish_internships=True,
            student_consent_given=True,
        )
        db.add(perm)
    else:
        perm.student_id = new_student.id
        perm.roll_no = new_student.roll_no
    db.commit()

    log_audit(db, current_user.id, current_user.username, "CREATE", "student", new_student.roll_no, f"Created student {new_student.full_name}")

    s_dict = {c.name: getattr(new_student, c.name) for c in new_student.__table__.columns}
    s_dict["internship_count"] = 0
    s_dict["is_public_approved"] = False
    return StudentOut(**s_dict)

@router.put("/{roll_no}", response_model=StudentOut)
def update_student(
    roll_no: str,
    student_in: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == roll_no, Student.is_deleted == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    update_data = student_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if hasattr(student, field):
            setattr(student, field, val)

    student.updated_by_user_id = current_user.id
    db.commit()

    log_audit(db, current_user.id, current_user.username, "UPDATE", "student", roll_no, f"Updated student {student.full_name}")

    i_cnt = db.query(func.count(Internship.id)).filter(
        Internship.roll_no == student.roll_no, Internship.is_deleted == False
    ).scalar() or 0
    perm = db.query(PublicProfilePermission).filter(PublicProfilePermission.student_id == student.id).first()

    s_dict = {c.name: getattr(student, c.name) for c in student.__table__.columns}
    s_dict["internship_count"] = i_cnt
    s_dict["is_public_approved"] = perm.is_public_approved if perm else False
    return StudentOut(**s_dict)

@router.delete("/{roll_no}")
def delete_student(
    roll_no: str,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == roll_no, Student.is_deleted == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.is_deleted = True
    student.updated_by_user_id = current_user.id
    db.commit()

    log_audit(db, current_user.id, current_user.username, "DELETE", "student", roll_no, f"Soft-deleted student {student.full_name}")
    return {"message": f"Student {roll_no} deleted successfully"}
