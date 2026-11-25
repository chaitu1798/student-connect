from pydantic import BaseModel, model_validator
from datetime import date, datetime

class InternshipBase(BaseModel):
    s_no: str | None = None
    roll_no: str
    full_name: str | None = None
    branch: str | None = None
    name_of_college: str | None = None
    college_name: str | None = None
    name_of_organization: str | None = None
    organization_name: str | None = None
    organization_district: str | None = None
    category: str | None = None
    role: str | None = None
    mode_of_internship: str | None = None
    mode: str | None = None
    internship_type: str | None = None
    stipend_amount: float | None = None
    stipend_range: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    certificate_received: str | None = "No"
    duration_weeks: int | None = None
    organization_address: str | None = None
    internship_offered_by: str | None = None
    offered_by: str | None = None
    regular_internship: str | None = None
    gender: str | None = None
    contact_number: str | None = None
    contact_no: str | None = None

    @model_validator(mode="before")
    @classmethod
    def populate_input_org_aliases(cls, data):
        if isinstance(data, dict):
            if "organization_name" in data and not data.get("name_of_organization"):
                data["name_of_organization"] = data["organization_name"]
            elif "name_of_organization" in data and not data.get("organization_name"):
                data["organization_name"] = data["name_of_organization"]
            if "mode" in data and not data.get("mode_of_internship"):
                data["mode_of_internship"] = data["mode"]
            elif "mode_of_internship" in data and not data.get("mode"):
                data["mode"] = data["mode_of_internship"]
            if "college_name" in data and not data.get("name_of_college"):
                data["name_of_college"] = data["college_name"]
            elif "name_of_college" in data and not data.get("college_name"):
                data["college_name"] = data["name_of_college"]
            if "offered_by" in data and not data.get("internship_offered_by"):
                data["internship_offered_by"] = data["offered_by"]
            elif "internship_offered_by" in data and not data.get("offered_by"):
                data["offered_by"] = data["internship_offered_by"]
            if "contact_no" in data and not data.get("contact_number"):
                data["contact_number"] = data["contact_no"]
            elif "contact_number" in data and not data.get("contact_no"):
                data["contact_no"] = data["contact_number"]
        return data

    @model_validator(mode="after")
    def populate_output_org_aliases(self):
        if not self.organization_name and self.name_of_organization:
            self.organization_name = self.name_of_organization
        if not self.name_of_organization and self.organization_name:
            self.name_of_organization = self.organization_name
        if not self.mode and self.mode_of_internship:
            self.mode = self.mode_of_internship
        if not self.mode_of_internship and self.mode:
            self.mode_of_internship = self.mode
        if not self.college_name and self.name_of_college:
            self.college_name = self.name_of_college
        if not self.name_of_college and self.college_name:
            self.name_of_college = self.college_name
        if not self.offered_by and self.internship_offered_by:
            self.offered_by = self.internship_offered_by
        if not self.internship_offered_by and self.offered_by:
            self.internship_offered_by = self.offered_by
        if not self.contact_no and self.contact_number:
            self.contact_no = self.contact_number
        if not self.contact_number and self.contact_no:
            self.contact_number = self.contact_no
        return self

class InternshipCreate(InternshipBase):
    pass

class InternshipPatch(BaseModel):
    s_no: str | None = None
    roll_no: str | None = None
    full_name: str | None = None
    branch: str | None = None
    name_of_college: str | None = None
    college_name: str | None = None
    name_of_organization: str | None = None
    organization_name: str | None = None
    organization_district: str | None = None
    role: str | None = None
    category: str | None = None
    mode_of_internship: str | None = None
    mode: str | None = None
    internship_type: str | None = None
    type: str | None = None
    stipend_amount: float | None = None
    stipend_range: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    certificate_received: str | None = None
    duration_weeks: int | None = None
    organization_address: str | None = None
    internship_offered_by: str | None = None
    offered_by: str | None = None
    regular_internship: str | None = None
    gender: str | None = None
    contact_number: str | None = None
    contact_no: str | None = None

class InternshipOut(InternshipBase):
    id: str
    student_id: str | None = None
    organization_id: str | None = None
    certificate_path: str | None = None
    certificate_file_path: str | None = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime | None = None

    @model_validator(mode="after")
    def populate_cert_aliases(self):
        if not self.certificate_file_path and self.certificate_path:
            self.certificate_file_path = self.certificate_path
        if not self.certificate_path and self.certificate_file_path:
            self.certificate_path = self.certificate_file_path
        return self

class InternshipListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[InternshipOut]

