import os
import shutil
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.student import Student, StudentPublicationSetting
from app.models.internship import Internship
from app.models.document import StudentDocument, InternshipCertificate
from app.routers.auth import get_current_user
from app.services.audit_service import log_audit
from app.utils.security import verify_file_signature

router = APIRouter(prefix="/documents", tags=["Document Management"])

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
ALLOWED_DOC_TYPES = ["application/pdf", "image/jpeg", "image/png"]

@router.post("/student/{roll_no}/upload")
async def upload_student_document(
    roll_no: str,
    doc_type: str = Form(..., description="'photo', 'aadhaar', or 'other'"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    student = db.query(Student).filter(Student.roll_no == roll_no, Student.is_archived == False).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Validate mime
    if doc_type in ["photo", "aadhaar"] and file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG/PNG images are allowed for Photo and Aadhaar card")

    subfolder = "photos" if doc_type == "photo" else ("aadhaar" if doc_type == "aadhaar" else "documents")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp", ".pdf"]:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    # Read and validate content size and magic signature
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB"
        )
    if not verify_file_signature(content, file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file signature or corrupted/disguised file"
        )

    safe_name = f"{roll_no}_{doc_type}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, subfolder, safe_name)

    with open(dest_path, "wb") as buffer:
        buffer.write(content)

    file_size = os.path.getsize(dest_path)
    rel_path = f"{subfolder}/{safe_name}"

    # Map document type
    doc_type_mapped = "PASSPORT_PHOTO" if doc_type.lower() == "photo" else ("AADHAAR" if doc_type.lower() == "aadhaar" else doc_type.upper())

    # If updating photo or aadhaar, delete or archive previous records to ensure latest authoritative record
    existing_docs = db.query(StudentDocument).filter(
        StudentDocument.student_id == student.id,
        StudentDocument.document_type == doc_type_mapped
    ).all()
    for ed in existing_docs:
        # Optionally remove older disk file if safe
        try:
            old_disk = os.path.join(settings.UPLOAD_DIR, ed.file_path.replace("/", os.sep))
            if os.path.exists(old_disk) and old_disk != dest_path:
                os.remove(old_disk)
        except Exception:
            pass
        db.delete(ed)

    # Record latest document entry
    doc = StudentDocument(
        student_id=student.id,
        roll_no=roll_no,
        document_type=doc_type_mapped,
        original_filename=file.filename,
        file_path=rel_path,
        file_size=file_size,
        mime_type=file.content_type,
        uploaded_by_user_id=current_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    student.updated_at = datetime.now(timezone.utc)
    db.commit()

    log_audit(db, current_user.id, current_user.username, "UPLOAD_DOC", "student", roll_no, f"Uploaded {doc_type} for {roll_no}")
    return {
        "message": "File uploaded successfully",
        "path": rel_path,
        "doc_id": doc.id,
        "photo_image_path": rel_path if doc_type_mapped == "PASSPORT_PHOTO" else None,
        "aadhaar_image_path": rel_path if doc_type_mapped == "AADHAAR" else None,
        "roll_no": roll_no
    }

@router.post("/internship/{internship_id}/certificate")
async def upload_internship_certificate(
    internship_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    internship = db.query(Internship).filter(
        (Internship.id == str(internship_id)) | (Internship.s_no == str(internship_id)),
        Internship.is_deleted == False
    ).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Only PDF, JPG, and PNG are allowed for certificates")

    # Read and validate content size and magic signature
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB"
        )
    if not verify_file_signature(content, file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file signature or corrupted/disguised file"
        )

    safe_name = f"internship_{internship_id}_{uuid.uuid4().hex[:8]}{ext}"
    dest_path = os.path.join(settings.UPLOAD_DIR, "certificates", safe_name)

    with open(dest_path, "wb") as buffer:
        buffer.write(content)

    rel_path = f"certificates/{safe_name}"
    internship.certificate_path = rel_path
    internship.certificate_received = "Yes"
    db.commit()

    log_audit(db, current_user.id, current_user.username, "UPLOAD_CERT", "internship", str(internship_id), f"Uploaded certificate for {internship.roll_no}")
    return {"message": "Certificate uploaded successfully", "path": rel_path}

@router.get("/photo/{filename}")
def serve_photo(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """
    Authenticated access to stored student photographs.
    Public access must use /api/v1/public/photo/{roll_number} which verifies publication approval.
    """
    clean = filename.replace("\\", "/").strip("/ ")
    if ".." in clean or os.path.isabs(clean) or ":" in clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid photo filename")
    
    upload_photos = os.path.abspath(os.path.join(settings.UPLOAD_DIR, "photos"))
    safe_path = os.path.abspath(os.path.join(upload_photos, os.path.basename(clean)))
    
    try:
        if os.path.commonpath([upload_photos, safe_path]) != upload_photos:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Path traversal detected")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Path traversal detected")

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(safe_path, headers={"Cache-Control": "private, max-age=0, must-revalidate"})

@router.get("/view")
def view_document_direct(
    path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure document viewing with Object-Level and Role-Based Authorization.
    Requires authentication, validates role permissions and object-level ownership,
    and strictly rejects path traversal.
    Aadhaar and sensitive identity cards are strictly forbidden on /view.
    """
    clean_path = (path or "").replace("\\", "/").strip("/ ")
    if clean_path.startswith("aadhaar/") or "_aadhaar_" in clean_path:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Aadhaar cards and sensitive identity documents cannot be viewed without administrator authentication."
        )
    return download_document(path=path, current_user=current_user, db=db)

@router.get("/download")
def download_document(
    path: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure document download/preview with Object-Level and Role-Based Authorization.
    - Path traversal attacks are rejected using strict commonpath verification.
    - Identity documents (Aadhaar) are strictly restricted to administrators.
    - Client access is restricted to authorized and public-consented documents.
    """
    if not path or ".." in path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document path")

    clean_path = path.replace("\\", "/").strip("/ ")
    if ".." in clean_path.split("/") or os.path.isabs(clean_path) or ":" in clean_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document path")

    upload_root = os.path.abspath(settings.UPLOAD_DIR)
    safe_path = os.path.abspath(os.path.join(upload_root, clean_path))
    
    # Path traversal check using commonpath
    try:
        common = os.path.commonpath([upload_root, safe_path])
        if common != upload_root:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Path traversal detected")
    except ValueError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: Path traversal detected")

    if not os.path.exists(safe_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document file not found")

    is_admin = (current_user.role or "").lower() in ["admin", "super_admin"]

    # Strict check for Aadhaar and private identity documents
    if clean_path.startswith("aadhaar/") or "_aadhaar_" in clean_path:
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Aadhaar cards and sensitive identity documents can only be accessed by authorized administrators."
            )

    # Object-level permission verification for non-admin client users
    if not is_admin:
        # Check student documents
        student_doc = db.query(StudentDocument).filter(
            (StudentDocument.file_path == clean_path) |
            (StudentDocument.file_path == clean_path.replace("/", "\\"))
        ).first()

        # Check internship certificates
        internship = db.query(Internship).filter(
            (Internship.certificate_path == clean_path) |
            (Internship.certificate_path == clean_path.replace("/", "\\"))
        ).first()

        if student_doc:
            if student_doc.document_type.lower() == "aadhaar":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Aadhaar cards and sensitive identity documents can only be accessed by authorized administrators."
                )
            if student_doc.document_type.lower() in ["other", "private", "id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not have permission to access this student's private document."
                )
            student = db.query(Student).filter(Student.id == student_doc.student_id).first()
            pub = student.publication_setting if student else None
            is_authorized = (
                student_doc.uploaded_by_user_id == current_user.id or
                (pub and pub.is_public_approved)
            )
            if not is_authorized:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not have permission to access this student's private document."
                )

        elif internship:
            student = db.query(Student).filter(Student.roll_no == internship.roll_no).first()
            pub = student.publication_setting if student else None
            is_authorized = (
                internship.created_by_user_id == current_user.id or
                (pub and pub.publish_internships and pub.is_public_approved)
            )
            if not is_authorized:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You do not have permission to access this internship certificate."
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Document record not verified in database."
            )

    log_audit(db, current_user.id, current_user.username, "DOWNLOAD_DOC", "file", clean_path, f"Downloaded {clean_path}")
    return FileResponse(safe_path)
