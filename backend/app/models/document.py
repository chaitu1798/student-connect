import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class StudentDocument(Base):
    __tablename__ = "student_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    roll_no = Column(String(50), nullable=True, index=True)
    document_type = Column(String(50), nullable=False)  # 'AADHAAR', 'PASSPORT_PHOTO', 'CERTIFICATE', 'RESUME', 'OTHER'
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_signature = Column(String(100), nullable=True)  # SHA256 checksum / magic byte verification
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="documents")

class InternshipCertificate(Base):
    __tablename__ = "internship_certificates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    internship_id = Column(String(36), nullable=True, index=True)
    roll_no = Column(String(50), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_by_user_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
