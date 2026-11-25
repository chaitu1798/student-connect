from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.pdf_service import process_pdf_upload, commit_pdf_extracted_data
from app.services.audit_service import log_audit
from app.utils.security import verify_file_signature

router = APIRouter(prefix="/pdf", tags=["PDF Extraction"])

@router.post("/extract")
async def upload_and_extract_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File exceeds 10MB limit")

    if not verify_file_signature(content, file.filename):
        raise HTTPException(status_code=400, detail="Invalid file signature. File is not a valid PDF document.")

    try:
        result = process_pdf_upload(db, content, file.filename, current_user.id)
        log_audit(db, current_user.id, current_user.username, "PDF_EXTRACT", "pdf", str(result["history_id"]), f"Uploaded and extracted {file.filename}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction error: {str(e)}")

@router.post("/commit/{history_id}")
def commit_extracted_pdf(
    history_id: int,
    reviewed_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        res = commit_pdf_extracted_data(db, history_id, reviewed_data, current_user.id)
        log_audit(db, current_user.id, current_user.username, "PDF_COMMIT", "pdf", str(history_id), f"Committed verified data for {reviewed_data.get('roll_no')}")
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
