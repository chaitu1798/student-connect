from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ImportJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    client_user_id: str | None = None
    file_name: str
    template_type: str
    status: str
    total_rows: int
    valid_rows: int
    diff_rows: int
    error_rows: int
    submitted_at: datetime | None = None
    reviewed_at: datetime | None = None
    remarks: str | None = None
    created_at: datetime

class ImportChangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    entity_type: str
    entity_id: str | None = None
    field_name: str
    old_value: str | None = None
    new_value: str | None = None
    is_selected: bool

class ImportRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    row_index: int
    roll_number: str | None = None
    status: str
    error_message: str | None = None
    normalized_data: dict | None = None
    changes: list[ImportChangeOut] = []

class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job: ImportJobOut
    rows: list[ImportRowOut]

class ApprovalRequest(BaseModel):
    remarks: str | None = None
