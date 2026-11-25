from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
import os
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.staging import ImportJob, ImportRow, ImportChange, ApprovalAction
from app.schemas.staging import (
    ImportJobOut,
    ImportRowOut,
    ImportChangeOut,
    ImportPreviewResponse,
    ApprovalRequest,
)
from app.routers.auth import require_role, get_current_user
from app.utils.security import verify_file_signature
from app.services.staging_service import (
    create_staged_import,
    apply_approved_job,
)
from app.services.excel_service import (
    read_excel_or_csv,
    map_headers,
    process_student_import,
    process_internship_import,
)
from app.services.audit_service import log_audit

router = APIRouter(tags=["Staged Import & Approval Engine"])

# --- Client Import Endpoints ---

@router.post("/client/imports", response_model=ImportJobOut, status_code=status.HTTP_201_CREATED)
async def upload_client_import(
    file: UploadFile = File(...),
    template_type: str = Form(..., description="'student' or 'internship'"),
    current_user: User = Depends(require_role(["CLIENT", "ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Client uploads a document (.xlsx, .xls, .csv, or .pdf).
    File signature verified, parsed into staging tables and diffs generated.
    Does NOT modify master records directly!
    """
    content = await file.read()
    try:
        job = create_staged_import(db, current_user.id, content, file.filename, template_type)
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/client/imports", response_model=list[ImportJobOut])
def list_client_imports(
    current_user: User = Depends(require_role(["CLIENT", "ADMIN", "SUPER_ADMIN", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    """Lists client's own import submissions with processing status."""
    query = db.query(ImportJob)
    if current_user.role == "CLIENT":
        query = query.filter(ImportJob.client_user_id == current_user.id)
    return query.order_by(ImportJob.created_at.desc()).limit(50).all()

@router.get("/client/imports/{id}", response_model=ImportJobOut)
def get_client_import_job(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return job

@router.get("/client/imports/{id}/preview", response_model=ImportPreviewResponse)
def get_import_preview(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns extracted rows, duplicate indicators, and detected diffs for client review."""
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    rows_out = []
    for r in job.rows:
        changes = [
            ImportChangeOut(
                id=c.id,
                entity_type=c.entity_type,
                entity_id=c.entity_id,
                field_name=c.field_name,
                old_value=c.old_value,
                new_value=c.new_value,
                is_selected=c.is_selected,
            )
            for c in r.changes
        ]
        norm = json.loads(r.normalized_data_json) if r.normalized_data_json else None
        rows_out.append(ImportRowOut(
            id=r.id,
            row_index=r.row_index,
            roll_number=r.roll_number,
            status=r.status,
            error_message=r.error_message,
            normalized_data=norm,
            changes=changes,
        ))

    return ImportPreviewResponse(job=ImportJobOut.model_validate(job), rows=rows_out)

@router.post("/client/imports/{id}/submit")
def submit_import_for_approval(
    id: str,
    current_user: User = Depends(require_role(["CLIENT", "ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    """Client submits reviewed staging job for administrator approval."""
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    if job.status not in ["DRAFT", "REJECTED"]:
        raise HTTPException(status_code=400, detail=f"Cannot submit job in '{job.status}' status")

    job.status = "SUBMITTED"
    job.submitted_at = datetime.now(timezone.utc)
    db.commit()

    log_audit(db, current_user.id, current_user.username, "SUBMIT_IMPORT", "import_job", job.id, f"Submitted import job {job.file_name} for approval")
    return {"message": "Import job submitted for administrator review and approval"}

# --- Direct Import Processing Endpoint (Excel/CSV) ---

@router.post("/imports/process")
async def process_direct_import(
    file: UploadFile = File(...),
    template_type: str = Form(..., description="'student' or 'internship'"),
    current_user: User = Depends(require_role(["ADMIN", "SUPER_ADMIN", "CLIENT"])),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".xlsx", ".xls", ".csv"]:
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are supported")

    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB"
        )

    if not verify_file_signature(content, file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file signature or corrupted/disguised file"
        )

    try:
        df = read_excel_or_csv(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse spreadsheet: {str(e)}")

    MAX_IMPORT_ROWS = 10000
    if len(df) > MAX_IMPORT_ROWS:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed limit of {MAX_IMPORT_ROWS} rows"
        )

    mapping = map_headers(list(df.columns), template_type)
    if template_type.lower() == "student":
        res = process_student_import(db, df, mapping, file.filename, current_user.id)
    else:
        res = process_internship_import(db, df, mapping, file.filename, current_user.id)
    return res

# --- Administrator Approval Endpoints ---

@router.get("/admin/imports", response_model=list[ImportJobOut])
def list_admin_pending_imports(
    status_filter: str = Query(None, description="Filter by status: SUBMITTED, APPROVED, REJECTED"),
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    query = db.query(ImportJob)
    if status_filter:
        query = query.filter(ImportJob.status == status_filter)
    return query.order_by(ImportJob.created_at.desc()).all()

@router.get("/admin/imports/{id}/diff")
def get_admin_import_diff(
    id: str,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    """
    Administrator reviews proposed changes (Old vs New value comparison)
    across all affected master student and internship records.
    """
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    diff_list = []
    for r in job.rows:
        if r.changes:
            for c in r.changes:
                diff_list.append({
                    "row_index": r.row_index,
                    "roll_number": r.roll_number,
                    "entity_type": c.entity_type,
                    "field_name": c.field_name,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                    "is_selected": c.is_selected,
                })

    return {
        "job_id": job.id,
        "file_name": job.file_name,
        "template_type": job.template_type,
        "status": job.status,
        "total_diff_changes": len(diff_list),
        "changes": diff_list,
    }

@router.post("/admin/imports/{id}/approve")
def approve_import(
    id: str,
    req: ApprovalRequest,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """
    Administrator approves import job. Changes are applied transactionally to master tables.
    """
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    if job.status not in ["SUBMITTED", "DRAFT"]:
        raise HTTPException(status_code=400, detail=f"Job status '{job.status}' cannot be approved")

    try:
        apply_approved_job(db, job, current_user.id, req.remarks)
        return {"message": f"Import job {job.file_name} approved and transactionally applied to master database"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Transactional commit failed: {str(e)}")

@router.post("/admin/imports/{id}/reject")
def reject_import(
    id: str,
    req: ApprovalRequest,
    current_user: User = Depends(require_role(["SUPER_ADMIN", "ADMIN", "REVIEWER"])),
    db: Session = Depends(get_db)
):
    """Administrator rejects import job with remarks."""
    job = db.query(ImportJob).filter(ImportJob.id == id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")

    job.status = "REJECTED"
    job.reviewed_at = datetime.now(timezone.utc)
    job.reviewed_by_user_id = current_user.id
    job.remarks = req.remarks or "Rejected by administrator"

    action = ApprovalAction(
        import_job_id=job.id,
        reviewer_id=current_user.id,
        action="REJECT",
        remarks=job.remarks,
    )
    db.add(action)
    db.commit()

    log_audit(db, current_user.id, current_user.username, "REJECT", "import_job", job.id, f"Rejected import {job.file_name}: {job.remarks}")
    return {"message": f"Import job {job.file_name} rejected"}
