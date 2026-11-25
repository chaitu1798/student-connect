import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Internship(Base):
    __tablename__ = "internships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    s_no = Column(String(50), nullable=True)
    roll_no = Column(String(50), index=True, nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id", ondelete="SET NULL"), index=True, nullable=True)

    full_name = Column(String(150), nullable=True)
    branch = Column(String(120), index=True, nullable=True)
    name_of_college = Column(String(200), nullable=True)
    name_of_organization = Column(String(200), index=True, nullable=False)
    organization_district = Column(String(100), index=True, nullable=True)
    category = Column(String(80), index=True, nullable=True)
    role = Column(String(120), nullable=True)
    mode_of_internship = Column(String(30), nullable=True)  # Online, Offline, Hybrid
    internship_type = Column(String(50), nullable=True)  # Paid, Unpaid
    stipend_amount = Column(Float, nullable=True)
    stipend_range = Column(String(60), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    certificate_received = Column(String(20), default="No", nullable=True)
    duration_weeks = Column(Integer, nullable=True)  # Auto-calculated using inclusive dates convention
    organization_address = Column(Text, nullable=True)
    internship_offered_by = Column(String(150), nullable=True)
    regular_internship = Column(String(60), nullable=True)  # AEP, IDEA LAB, Regular
    gender = Column(String(20), nullable=True)
    contact_number = Column(String(30), nullable=True)
    certificate_path = Column(String(255), nullable=True)

    is_deleted = Column(Boolean, default=False, nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="internships")
    organization_rel = relationship("Organization", back_populates="internships")

Index("idx_internships_roll_org", Internship.roll_no, Internship.name_of_organization)
