import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.crypto import EncryptedField

class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    s_no = Column(String(50), nullable=True)
    roll_no = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(150), index=True, nullable=False)
    first_name = Column(String(80), nullable=True)
    middle_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)

    college_id = Column(String(36), ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True)
    branch_id = Column(String(36), ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)

    # Denormalized convenience strings matching original forms
    branch = Column(String(120), index=True, nullable=True)
    branch_code = Column(String(30), index=True, nullable=True)
    name_of_college = Column(String(200), nullable=True)

    # Legacy field preserved exactly as specified
    column1 = Column(Text, nullable=True)

    is_archived = Column(Boolean, default=False, nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships to normalized tables
    college = relationship("College", back_populates="students")
    branch_rel = relationship("Branch", back_populates="students")
    contacts = relationship("StudentContact", back_populates="student", uselist=False, cascade="all, delete-orphan")
    academics = relationship("StudentAcademic", back_populates="student", uselist=False, cascade="all, delete-orphan")
    private_data = relationship("StudentPrivateData", back_populates="student", uselist=False, cascade="all, delete-orphan")
    addresses = relationship("StudentAddress", back_populates="student", uselist=False, cascade="all, delete-orphan")
    documents = relationship("StudentDocument", back_populates="student", cascade="all, delete-orphan")
    consent = relationship("StudentConsent", back_populates="student", uselist=False, cascade="all, delete-orphan")
    publication_setting = relationship("StudentPublicationSetting", back_populates="student", uselist=False, cascade="all, delete-orphan")
    internships = relationship("Internship", back_populates="student", cascade="all, delete-orphan")

class StudentContact(Base):
    __tablename__ = "student_contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    recorded_email = Column(String(120), nullable=True)
    corrected_placement_email = Column(String(120), nullable=True)
    alternate_personal_email = Column(String(120), nullable=True)
    contact_number = Column(String(30), nullable=True)
    parent_contact_number = Column(String(30), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="contacts")

class StudentAcademic(Base):
    __tablename__ = "student_academics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # UG
    ug_cgpa = Column(Float, nullable=True)
    ug_year_of_passing = Column(Integer, index=True, nullable=True)
    number_of_backlogs = Column(Integer, default=0, nullable=True)
    crt_registered = Column(String(10), default="N", nullable=True)

    # SSC / 10th
    x_grading_system = Column(String(40), nullable=True)
    x_cgpa_percentage = Column(String(40), nullable=True)
    x_year_of_passing = Column(Integer, nullable=True)
    x_school_name = Column(String(200), nullable=True)

    # Inter / Diploma
    study_after_x = Column(String(60), nullable=True)
    xii_grading_system = Column(String(40), nullable=True)
    xii_cgpa_percentage = Column(String(40), nullable=True)
    xii_year_of_passing = Column(Integer, nullable=True)
    xii_college_name = Column(String(200), nullable=True)

    # Admission
    admission_type = Column(String(60), nullable=True)
    entrance_exam = Column(String(60), nullable=True)
    entrance_rank = Column(String(40), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="academics")

class StudentPrivateData(Base):
    __tablename__ = "student_private_data"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    gender = Column(String(20), nullable=True)
    date_of_birth = Column(String(30), nullable=True)
    languages_known = Column(String(150), nullable=True)
    father_name = Column(String(120), nullable=True)
    father_occupation = Column(String(100), nullable=True)
    caste = Column(String(60), nullable=True)

    # Shielded identifiers (Authenticated AES-256-GCM encryption at rest)
    pan_number = Column(EncryptedField(255), nullable=True)
    aadhaar_number = Column(EncryptedField(255), nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="private_data")

class StudentAddress(Base):
    __tablename__ = "student_addresses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    full_residential_address = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("Student", back_populates="addresses")

class StudentConsent(Base):
    __tablename__ = "student_consents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    consent_given = Column(Boolean, default=True, nullable=False)
    consent_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    consent_details = Column(Text, nullable=True)

    student = relationship("Student", back_populates="consent")

class StudentPublicationSetting(Base):
    __tablename__ = "student_publication_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    is_public_approved = Column(Boolean, default=False, nullable=False, index=True)
    publish_gender = Column(Boolean, default=False, nullable=False)
    publish_cgpa = Column(Boolean, default=False, nullable=False)
    publish_internships = Column(Boolean, default=True, nullable=False)
    approved_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="publication_setting")
