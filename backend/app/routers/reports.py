from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.report_service import (
    generate_report_dataframe,
    export_report_excel,
    export_report_csv,
    export_report_pdf,
)
from app.services.audit_service import log_audit

router = APIRouter(prefix="/reports", tags=["Reports & Exports"])

VALID_REPORTS = [
    "complete_student",
    "academic",
    "internship",
    "organization_wise",
    "crt_registered",
    "backlog",
    "without_internships",
    "certificate_pending",
]

@router.get("/export")
def export_report(
    report_type: str = Query(..., description="Report type identifier"),
    format: str = Query("excel", pattern="^(excel|csv|pdf)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if report_type not in VALID_REPORTS:
        raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {', '.join(VALID_REPORTS)}")

    is_admin = (current_user.role or "").upper() in ["SUPER_ADMIN", "ADMIN"]
    if report_type == "complete_student" and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Exporting complete student records is restricted to administrators."
        )

    df = generate_report_dataframe(db, report_type, mask_sensitive=not is_admin)
    title = report_type.replace("_", " ").title() + " Report"

    log_audit(db, current_user.id, current_user.username, "EXPORT", "report", report_type, f"Exported {report_type} in {format} format")

    if format == "excel":
        file_bytes = export_report_excel(df, title)
        return Response(
            content=file_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.xlsx"}
        )
    elif format == "csv":
        file_bytes = export_report_csv(df)
        return Response(
            content=file_bytes,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"}
        )
    elif format == "pdf":
        file_bytes = export_report_pdf(df, title)
        return Response(
            content=file_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={report_type}_report.pdf"}
        )
