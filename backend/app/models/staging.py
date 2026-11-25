import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    file_name = Column(String(255), nullable=False)
    template_type = Column(String(40), nullable=False)  # 'student' or 'internship'
    status = Column(String(40), default="DRAFT", index=True, nullable=False)  # DRAFT, SUBMITTED, APPROVED, REJECTED, APPLIED
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    error_rows = Column(Integer, default=0)
    diff_rows = Column(Integer, default=0)
    remarks = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    rows = relationship("ImportRow", back_populates="import_job", cascade="all, delete-orphan")
    approval_actions = relationship("ApprovalAction", back_populates="import_job", cascade="all, delete-orphan")

class ImportRow(Base):
    __tablename__ = "import_rows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_job_id = Column(String(36), ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    row_index = Column(Integer, nullable=False)
    roll_number = Column(String(50), index=True, nullable=True)
    status = Column(String(40), default="VALID", index=True)  # VALID, ERROR, DIFF_DETECTED
    raw_data_json = Column(Text, nullable=True)  # Source spreadsheet row in JSON
    normalized_data_json = Column(Text, nullable=True)  # Normalized target fields in JSON
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    import_job = relationship("ImportJob", back_populates="rows")
    changes = relationship("ImportChange", back_populates="import_row", cascade="all, delete-orphan")

class ImportChange(Base):
    __tablename__ = "import_changes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_row_id = Column(String(36), ForeignKey("import_rows.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = Column(String(40), nullable=False)  # 'student', 'academic', 'contact', 'internship'
    entity_id = Column(String(80), nullable=True)
    field_name = Column(String(80), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    is_selected = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    import_row = relationship("ImportRow", back_populates="changes")

class ImportColumnMapping(Base):
    __tablename__ = "import_column_mappings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    template_type = Column(String(40), nullable=False, index=True)
    source_column = Column(String(120), nullable=False)
    target_field = Column(String(80), nullable=False)

class ApprovalAction(Base):
    __tablename__ = "approval_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    import_job_id = Column(String(36), ForeignKey("import_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(30), nullable=False)  # 'APPROVE', 'REJECT'
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    import_job = relationship("ImportJob", back_populates="approval_actions")
