from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.internship import Internship
from app.models.organization import Organization
from app.schemas.internship import InternshipCreate, InternshipPatch, InternshipOut, InternshipListResponse
from app.routers.auth import require_role
from app.services.audit_service import log_audit
from app.utils.security import calculate_duration_weeks

router = APIRouter(tags=["Internships"])

@router.get("/internships", response_model=InternshipListResponse)
def list_public_internships(
    roll_no: Optional[str] = Query(None),
    search: str = Query("", description="Company, Role, or Student Name"),
    category: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    certificate_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Internship).filter(Internship.is_deleted == False)

    if roll_no:
        query = query.filter(Internship.roll_no == roll_no.strip())
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(
            Internship.name_of_organization.ilike(term),
            Internship.role.ilike(term),
            Internship.full_name.ilike(term),
            Internship.roll_no.ilike(term),
        ))
    if category and category.strip():
        query = query.filter(Internship.category.ilike(f"%{category.strip()}%"))
    if mode and mode.strip():
        query = query.filter(Internship.mode_of_internship.ilike(f"%{mode.strip()}%"))
    if type and type.strip():
        query = query.filter(Internship.internship_type.ilike(f"%{type.strip()}%"))
    if branch and branch.strip():
        query = query.filter(Internship.branch.ilike(f"%{branch.strip()}%"))
    if district and district.strip():
        query = query.filter(Internship.organization_district.ilike(f"%{district.strip()}%"))
    if certificate_status and certificate_status.strip():
        query = query.filter(Internship.certificate_received.ilike(f"%{certificate_status.strip()}%"))

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Internship.id.desc()).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

@router.get("/admin/internships", response_model=InternshipListResponse)
def list_admin_internships(
    roll_no: Optional[str] = Query(None),
    search: str = Query("", description="Company, Role, or Student Name"),
    category: Optional[str] = Query(None),
    mode: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    branch: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    certificate_status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER", "CLIENT"])),
    db: Session = Depends(get_db)
):
    query = db.query(Internship).filter(Internship.is_deleted == False)

    if roll_no:
        query = query.filter(Internship.roll_no == roll_no.strip())
    if search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(or_(
            Internship.name_of_organization.ilike(term),
            Internship.role.ilike(term),
            Internship.full_name.ilike(term),
            Internship.roll_no.ilike(term),
        ))
    if category and category.strip():
        query = query.filter(Internship.category.ilike(f"%{category.strip()}%"))
    if mode and mode.strip():
        query = query.filter(Internship.mode_of_internship.ilike(f"%{mode.strip()}%"))
    if type and type.strip():
        query = query.filter(Internship.internship_type.ilike(f"%{type.strip()}%"))
    if branch and branch.strip():
        query = query.filter(Internship.branch.ilike(f"%{branch.strip()}%"))
    if district and district.strip():
        query = query.filter(Internship.organization_district.ilike(f"%{district.strip()}%"))
    if certificate_status and certificate_status.strip():
        query = query.filter(Internship.certificate_received.ilike(f"%{certificate_status.strip()}%"))

    total = query.count()
    offset = (page - 1) * page_size
    items = query.order_by(Internship.id.desc()).offset(offset).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items,
    }

@router.get("/internships/statistics")
@router.get("/admin/internships/statistics")
def get_internship_statistics(db: Session = Depends(get_db)):
    base_query = db.query(Internship).filter(Internship.is_deleted == False)
    total = base_query.count()

    total_orgs = (
        db.query(func.count(func.distinct(Internship.name_of_organization)))
        .filter(Internship.is_deleted == False)
        .scalar() or 0
    )

    # Branch-wise
    branch_rows = (
        db.query(Internship.branch, func.count(Internship.id))
        .filter(Internship.is_deleted == False, Internship.branch.isnot(None), Internship.branch != "")
        .group_by(Internship.branch)
        .order_by(func.count(Internship.id).desc())
        .all()
    )
    branch_wise = [{"branch": r[0], "count": r[1]} for r in branch_rows]

    # Organization-wise (top 15)
    org_rows = (
        db.query(Internship.name_of_organization, func.count(Internship.id))
        .filter(Internship.is_deleted == False, Internship.name_of_organization.isnot(None), Internship.name_of_organization != "")
        .group_by(Internship.name_of_organization)
        .order_by(func.count(Internship.id).desc())
        .limit(15)
        .all()
    )
    org_wise = [{"organization": r[0], "count": r[1]} for r in org_rows]

    # District-wise
    district_rows = (
        db.query(Internship.organization_district, func.count(Internship.id))
        .filter(Internship.is_deleted == False, Internship.organization_district.isnot(None), Internship.organization_district != "")
        .group_by(Internship.organization_district)
        .order_by(func.count(Internship.id).desc())
        .all()
    )
    district_wise = [{"district": r[0], "count": r[1]} for r in district_rows]

    # Certificate status
    cert_received = base_query.filter(Internship.certificate_received.ilike("Yes%")).count()
    cert_pending = total - cert_received

    # Mode wise
    mode_rows = (
        db.query(Internship.mode_of_internship, func.count(Internship.id))
        .filter(Internship.is_deleted == False)
        .group_by(Internship.mode_of_internship)
        .all()
    )
    mode_wise = {r[0] or "Unspecified": r[1] for r in mode_rows}

    # Type wise
    type_rows = (
        db.query(Internship.internship_type, func.count(Internship.id))
        .filter(Internship.is_deleted == False)
        .group_by(Internship.internship_type)
        .all()
    )
    type_wise = {r[0] or "Unspecified": r[1] for r in type_rows}

    # Stipend stats
    paid_count = base_query.filter(Internship.stipend_amount > 0).count()
    avg_stipend = (
        db.query(func.avg(Internship.stipend_amount))
        .filter(Internship.is_deleted == False, Internship.stipend_amount > 0)
        .scalar() or 0.0
    )
    max_stipend = (
        db.query(func.max(Internship.stipend_amount))
        .filter(Internship.is_deleted == False, Internship.stipend_amount > 0)
        .scalar() or 0.0
    )
    avg_duration = (
        db.query(func.avg(Internship.duration_weeks))
        .filter(Internship.is_deleted == False, Internship.duration_weeks > 0)
        .scalar() or 0.0
    )

    return {
        "total": total,
        "total_organizations": total_orgs,
        "branch_wise": branch_wise,
        "organization_wise": org_wise,
        "district_wise": district_wise,
        "certificate_status": {
            "received": cert_received,
            "pending": cert_pending,
            "received_percentage": round((cert_received / total * 100) if total > 0 else 0, 1)
        },
        "mode_wise": mode_wise,
        "type_wise": type_wise,
        "stipend_stats": {
            "paid_count": paid_count,
            "unpaid_count": total - paid_count,
            "avg_stipend": round(float(avg_stipend), 2),
            "max_stipend": round(float(max_stipend), 2),
            "avg_duration_weeks": round(float(avg_duration), 1)
        }
    }

@router.get("/internships/{id}", response_model=InternshipOut)
@router.get("/admin/internships/{id}", response_model=InternshipOut)
def get_internship_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    item = db.query(Internship).filter(Internship.id == id, Internship.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")
    return item

@router.post("/internships", response_model=InternshipOut, status_code=status.HTTP_201_CREATED)
@router.post("/admin/internships", response_model=InternshipOut, status_code=status.HTTP_201_CREATED)
def create_internship(
    data: InternshipCreate,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == data.roll_no).first()

    org_name = data.name_of_organization or data.organization_name or "General Partner"

    # Find or create organization
    org = db.query(Organization).filter(Organization.name == org_name).first()
    if not org:
        org = Organization(
            name=org_name,
            district=data.organization_district,
            address=data.organization_address,
            category=data.category,
        )
        db.add(org)
        db.flush()

    duration = data.duration_weeks
    if not duration and data.start_date and data.end_date:
        duration = calculate_duration_weeks(data.start_date, data.end_date)

    college = data.name_of_college or data.college_name
    offered = data.internship_offered_by or data.offered_by
    contact = data.contact_number or data.contact_no

    gender_val = data.gender
    contact_val = contact
    if student:
        if not gender_val and hasattr(student, "private_data") and student.private_data:
            gender_val = student.private_data.gender
        if not contact_val and hasattr(student, "contacts") and student.contacts:
            contact_val = student.contacts.contact_number

    internship = Internship(
        s_no=data.s_no,
        student_id=student.id if student else None,
        organization_id=org.id,
        roll_no=data.roll_no,
        full_name=data.full_name or (student.full_name if student else None),
        branch=data.branch or (student.branch if student else None),
        name_of_college=college or (student.name_of_college if student else None),
        name_of_organization=org_name,
        organization_district=data.organization_district,
        category=data.category,
        role=data.role,
        mode_of_internship=data.mode_of_internship or data.mode or "Offline",
        internship_type=data.internship_type or "Paid",
        stipend_amount=data.stipend_amount,
        stipend_range=data.stipend_range,
        start_date=data.start_date,
        end_date=data.end_date,
        duration_weeks=duration,
        certificate_received=data.certificate_received or "No",
        organization_address=data.organization_address,
        internship_offered_by=offered,
        regular_internship=data.regular_internship,
        gender=gender_val,
        contact_number=contact_val,
        created_by_user_id=current_user.id,
    )
    db.add(internship)
    db.commit()
    db.refresh(internship)

    log_audit(db, current_user.id, current_user.username, "CREATE", "internship", internship.id, f"Created internship at {internship.name_of_organization}")
    return internship

@router.put("/internships/{id}", response_model=InternshipOut)
@router.patch("/internships/{id}", response_model=InternshipOut)
@router.put("/admin/internships/{id}", response_model=InternshipOut)
@router.patch("/admin/internships/{id}", response_model=InternshipOut)
def patch_internship(
    id: str,
    patch_in: InternshipPatch,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    item = db.query(Internship).filter(Internship.id == id, Internship.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")

    p = patch_in.model_dump(exclude_unset=True)
    if "organization_name" in p and "name_of_organization" not in p:
        p["name_of_organization"] = p["organization_name"]
    if "mode" in p and "mode_of_internship" not in p:
        p["mode_of_internship"] = p["mode"]
    if "type" in p and "internship_type" not in p:
        p["internship_type"] = p["type"]
    if "college_name" in p and "name_of_college" not in p:
        p["name_of_college"] = p["college_name"]
    if "offered_by" in p and "internship_offered_by" not in p:
        p["internship_offered_by"] = p["offered_by"]
    if "contact_no" in p and "contact_number" not in p:
        p["contact_number"] = p["contact_no"]

    for k, v in p.items():
        if hasattr(item, k):
            setattr(item, k, v)

    if item.start_date and item.end_date:
        item.duration_weeks = calculate_duration_weeks(item.start_date, item.end_date)

    item.updated_by_user_id = current_user.id
    db.commit()
    db.refresh(item)

    log_audit(db, current_user.id, current_user.username, "PATCH", "internship", item.id, f"Updated internship {item.name_of_organization}")
    return item

@router.delete("/internships/{id}")
@router.delete("/admin/internships/{id}")
def delete_internship(
    id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    item = db.query(Internship).filter(Internship.id == id, Internship.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Internship not found")

    item.is_deleted = True
    item.updated_by_user_id = current_user.id
    db.commit()

    log_audit(db, current_user.id, current_user.username, "DELETE", "internship", item.id, f"Deleted internship at {item.name_of_organization}")
    return {"message": "Internship deleted successfully"}

