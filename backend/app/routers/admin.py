from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.models.organization import Branch
from app.models.student import Student, StudentPublicationSetting
from app.schemas.auth import UserCreate, UserOut
from app.schemas.report import PublicProfilePermissionUpdate, PublicPermissionOut
from app.routers.auth import require_role
from app.utils.security import hash_password
from app.services.audit_service import log_audit

router = APIRouter(prefix="/admin", tags=["Administrator Dashboard & Governance"])

# Client account management
@router.get("/clients", response_model=list[UserOut])
def list_clients(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    return db.query(User).filter(User.role == "CLIENT").order_by(User.created_at.desc()).all()

@router.post("/clients", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: UserCreate,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == client_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == client_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=client_in.username,
        email=client_in.email,
        full_name=client_in.full_name,
        role="CLIENT",
        hashed_password=hash_password(client_in.password),
        must_change_password=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_audit(db, current_user.id, current_user.username, "CREATE", "user", new_user.id, f"Created client {new_user.username}")
    return new_user

@router.put("/clients/{client_id}")
def toggle_client_status(
    client_id: str,
    is_active: bool,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == client_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    db.commit()
    log_audit(db, current_user.id, current_user.username, "UPDATE_STATUS", "user", user.id, f"Set active={is_active}")
    return {"message": "User status updated"}

@router.post("/clients/{client_id}/reset-password")
def reset_client_password(
    client_id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == client_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    temp_password = "Password123!"
    user.hashed_password = hash_password(temp_password)
    user.must_change_password = True
    db.commit()

    log_audit(db, current_user.id, current_user.username, "RESET_PWD", "user", user.id, f"Reset password for {user.username}")
    return {"message": "Password reset successfully", "temporary_password": temp_password}

# Public Profile Permissions & Approvals
@router.get("/permissions")
def list_public_permissions(
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    students = db.query(Student).filter(Student.is_archived == False).order_by(Student.roll_no.asc()).all()
    items = []
    for s in students:
        pub = s.publication_setting
        items.append({
            "id": pub.id if pub else s.id,
            "student_id": s.id,
            "roll_no": s.roll_no,
            "student_name": s.full_name,
            "branch": s.branch,
            "is_public_approved": pub.is_public_approved if pub else False,
            "publish_gender": pub.publish_gender if pub else False,
            "publish_cgpa": pub.publish_cgpa if pub else False,
            "publish_internships": pub.publish_internships if pub else True,
            "student_consent_given": True,
        })
    return items

@router.put("/permissions/{roll_no}")
def update_public_permission(
    roll_no: str,
    update_in: PublicProfilePermissionUpdate,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == roll_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    pub = student.publication_setting
    if not pub:
        pub = StudentPublicationSetting(student_id=student.id)
        db.add(pub)

    pub.is_public_approved = update_in.is_public_approved
    pub.publish_gender = update_in.publish_gender
    pub.publish_cgpa = update_in.publish_cgpa
    pub.publish_internships = update_in.publish_internships
    pub.approved_by_user_id = current_user.id
    pub.approved_at = datetime.now(timezone.utc)
    db.commit()

    log_audit(db, current_user.id, current_user.username, "APPROVE_PROFILE", "permission", roll_no, f"Updated public profile status for {roll_no}: approved={update_in.is_public_approved}")
    return {"message": f"Updated public permission for {roll_no}"}

# System Audit Logs
@router.get("/audit-logs")
def get_audit_logs(
    action: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": log.id,
                "username": log.username,
                "action": log.action,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in items
        ]
    }
