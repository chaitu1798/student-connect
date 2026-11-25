from pydantic import BaseModel, ConfigDict

class DashboardStats(BaseModel):
    total_students: int
    total_internships: int
    total_clients: int
    total_branches: int
    students_with_backlogs: int
    crt_registered_count: int
    students_without_internships: int
    recently_updated_students: list[dict] = []
    branch_distribution: dict[str, int] = {}
    year_distribution: dict[str, int] = {}
    gender_distribution: dict[str, int] = {}
    organization_distribution: dict[str, int] = {}
    stipend_range_distribution: dict[str, int] = {}

class PublicProfilePermissionUpdate(BaseModel):
    is_public_approved: bool
    publish_gender: bool = False
    publish_cgpa: bool = False
    publish_internships: bool = True
    student_consent_given: bool = True

class PublicPermissionOut(BaseModel):
    id: int
    student_id: int
    roll_no: str
    student_name: str
    branch: str | None = None
    is_public_approved: bool
    publish_gender: bool
    publish_cgpa: bool
    publish_internships: bool
    student_consent_given: bool

    model_config = ConfigDict(from_attributes=True)
