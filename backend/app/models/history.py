from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime, timezone
from app.database import Base

class ExcelImportHistory(Base):
    __tablename__ = "excel_import_history"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    template_type = Column(String(30), nullable=False)  # 'student' or 'internship'
    total_rows = Column(Integer, default=0)
    inserted_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    duplicate_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    failed_records_json = Column(Text, nullable=True)  # JSON string of errors/failed rows
    status = Column(String(30), default="completed")  # completed, partial, failed
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PdfUploadHistory(Base):
    __tablename__ = "pdf_upload_history"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    extracted_data_json = Column(Text, nullable=True)  # JSON extracted fields
    matched_roll_no = Column(String(50), nullable=True, index=True)
    status = Column(String(30), default="extracted")  # extracted, reviewed, committed, failed
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
