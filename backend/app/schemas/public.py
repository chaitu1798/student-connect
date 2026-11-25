from pydantic import BaseModel

class PublicApprovedInternship(BaseModel):
    organization_name: str
    organization_district: str | None = None
    role: str | None = None
    category: str | None = None
    mode: str | None = None
    duration_weeks: int | None = None
    regular_internship: str | None = None

class PublicStudentProfile(BaseModel):
    full_name: str
    roll_no: str
    branch: str | None = None
    branch_code: str | None = None
    gender: str | None = None  # Included ONLY if publish_gender is True
    ug_cgpa: float | None = None  # Included ONLY if publish_cgpa is True
    ug_year_of_pass: int | None = None
    internship_count: int
    internships: list[PublicApprovedInternship] = []

class PublicStudentSummary(BaseModel):
    roll_no: str
    full_name: str
    branch: str | None = None
    branch_code: str | None = None
    ug_year_of_pass: int | None = None
    internship_count: int

class PublicSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PublicStudentSummary]

class PublicStats(BaseModel):
    total_students: int
    total_internships: int
    total_branches: int
    branch_statistics: dict[str, int]
    recent_approved_profiles: list[PublicStudentSummary]
    internship_highlights: list[dict]
