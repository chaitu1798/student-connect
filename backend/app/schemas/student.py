from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime
from typing import Any

class StudentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    s_no: str | None = None
    roll_no: str
    full_name: str
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    branch: str | None = None
    branch_code: str | None = None
    name_of_college: str | None = None
    column1: str | None = None  # Legacy field preserved

    # Contact
    recorded_email: str | None = None
    corrected_placement_email: str | None = None
    alternate_personal_email: str | None = None
    contact_number: str | None = None
    parent_contact_number: str | None = None

    # Academic
    ug_cgpa: float | None = None
    ug_year_of_passing: int | None = None
    number_of_backlogs: int | None = 0
    crt_registered: str | None = "N"

    # SSC
    x_grading_system: str | None = None
    x_cgpa_percentage: str | None = None
    x_year_of_passing: int | None = None
    x_school_name: str | None = None

    # Inter / Diploma
    study_after_x: str | None = None
    xii_grading_system: str | None = None
    xii_cgpa_percentage: str | None = None
    xii_year_of_passing: int | None = None
    xii_college_name: str | None = None

    # Admission
    admission_type: str | None = None
    entrance_exam: str | None = None
    entrance_rank: str | None = None

    # Personal & Family
    gender: str | None = None
    date_of_birth: str | None = None
    languages_known: str | None = None
    father_name: str | None = None
    father_occupation: str | None = None
    caste: str | None = None

    # Address & ID
    full_residential_address: str | None = None
    pan_number: str | None = None
    aadhaar_number: str | None = None

    # Documents
    photo_image_path: str | None = None
    aadhaar_image_path: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_synonyms(cls, data: Any) -> Any:
        if isinstance(data, dict):
            # Map frontend property variations
            if "contact_no" in data and not data.get("contact_number"):
                data["contact_number"] = data["contact_no"]
            if "parent_contact_no" in data and not data.get("parent_contact_number"):
                data["parent_contact_number"] = data["parent_contact_no"]
            if "corrected_placements_email" in data and not data.get("corrected_placement_email"):
                data["corrected_placement_email"] = data["corrected_placements_email"]
            if "ug_year_of_pass" in data and not data.get("ug_year_of_passing"):
                data["ug_year_of_passing"] = data["ug_year_of_pass"]
            if "no_of_backlogs" in data and "number_of_backlogs" not in data:
                data["number_of_backlogs"] = data["no_of_backlogs"]
            if "residential_address" in data and not data.get("full_residential_address"):
                data["full_residential_address"] = data["residential_address"]
            if "x_year_of_pass" in data and not data.get("x_year_of_passing"):
                data["x_year_of_passing"] = data["x_year_of_pass"]
            if "xii_percentage_cgpa" in data and not data.get("xii_cgpa_percentage"):
                data["xii_cgpa_percentage"] = data["xii_percentage_cgpa"]
            if "xii_year_of_pass" in data and not data.get("xii_year_of_passing"):
                data["xii_year_of_passing"] = data["xii_year_of_pass"]
        return data

class StudentCreate(StudentBase):
    pass

class StudentPatch(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    s_no: str | None = None
    full_name: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    branch: str | None = None
    branch_code: str | None = None
    name_of_college: str | None = None
    column1: str | None = None
    ug_cgpa: float | None = None
    ug_year_of_passing: int | None = None
    ug_year_of_pass: int | None = None
    number_of_backlogs: int | None = None
    no_of_backlogs: int | None = None
    crt_registered: str | None = None
    contact_number: str | None = None
    contact_no: str | None = None
    parent_contact_number: str | None = None
    parent_contact_no: str | None = None
    recorded_email: str | None = None
    corrected_placement_email: str | None = None
    corrected_placements_email: str | None = None
    alternate_personal_email: str | None = None
    gender: str | None = None
    date_of_birth: str | None = None
    x_grading_system: str | None = None
    x_cgpa_percentage: str | None = None
    x_year_of_passing: int | None = None
    x_school_name: str | None = None
    study_after_x: str | None = None
    xii_grading_system: str | None = None
    xii_cgpa_percentage: str | None = None
    xii_year_of_passing: int | None = None
    xii_college_name: str | None = None
    admission_type: str | None = None
    entrance_exam: str | None = None
    entrance_rank: str | None = None
    father_name: str | None = None
    father_occupation: str | None = None
    languages_known: str | None = None
    caste: str | None = None
    full_residential_address: str | None = None
    residential_address: str | None = None
    pan_number: str | None = None
    aadhaar_number: str | None = None
    photo_image_path: str | None = None
    aadhaar_image_path: str | None = None

    @model_validator(mode="before")
    @classmethod
    def normalize_patch_synonyms(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "contact_no" in data and not data.get("contact_number"):
                data["contact_number"] = data["contact_no"]
            if "parent_contact_no" in data and not data.get("parent_contact_number"):
                data["parent_contact_number"] = data["parent_contact_no"]
            if "corrected_placements_email" in data and not data.get("corrected_placement_email"):
                data["corrected_placement_email"] = data["corrected_placements_email"]
            if "ug_year_of_pass" in data and not data.get("ug_year_of_passing"):
                data["ug_year_of_passing"] = data["ug_year_of_pass"]
            if "no_of_backlogs" in data and "number_of_backlogs" not in data:
                data["number_of_backlogs"] = data["no_of_backlogs"]
            if "residential_address" in data and not data.get("full_residential_address"):
                data["full_residential_address"] = data["residential_address"]
            if "x_year_of_pass" in data and not data.get("x_year_of_passing"):
                data["x_year_of_passing"] = data["x_year_of_pass"]
            if "xii_percentage_cgpa" in data and not data.get("xii_cgpa_percentage"):
                data["xii_cgpa_percentage"] = data["xii_percentage_cgpa"]
            if "xii_year_of_pass" in data and not data.get("xii_year_of_passing"):
                data["xii_year_of_passing"] = data["xii_year_of_pass"]
        return data

StudentUpdate = StudentPatch

class StudentOut(StudentBase):
    id: str
    is_archived: bool
    internship_count: int = 0
    is_public_approved: bool = False
    created_at: datetime
    updated_at: datetime | None = None

    # Synonyms returned for convenience to guarantee matching with frontend property names
    contact_no: str | None = None
    parent_contact_no: str | None = None
    corrected_placements_email: str | None = None
    ug_year_of_pass: int | None = None
    no_of_backlogs: int | None = 0
    residential_address: str | None = None
    x_year_of_pass: int | None = None
    xii_percentage_cgpa: str | None = None
    xii_year_of_pass: int | None = None

class StudentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[StudentOut]

class PublicStudentSummary(BaseModel):
    roll_no: str
    full_name: str
    branch: str | None = None
    branch_code: str | None = None
    ug_year_of_passing: int | None = None
    ug_year_of_pass: int | None = None
    internship_count: int
    photo_image_path: str | None = None

class PublicStudentDetail(BaseModel):
    full_name: str
    roll_no: str
    branch: str | None = None
    branch_code: str | None = None
    gender: str | None = None
    ug_cgpa: float | None = None
    ug_year_of_passing: int | None = None
    ug_year_of_pass: int | None = None
    internship_count: int
    internships: list[dict] = []
    photo_image_path: str | None = None

class PublicSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PublicStudentSummary]
