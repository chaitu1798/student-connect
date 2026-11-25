from pydantic import BaseModel
from datetime import datetime

class ExcelImportPreviewRequest(BaseModel):
    template_type: str  # 'student' or 'internship'

class ExcelImportSummary(BaseModel):
    history_id: int
    template_type: str
    total_records: int
    inserted_count: int
    updated_count: int
    duplicate_count: int
    failed_count: int
    failed_records: list[dict] = []
    message: str

class ImportHistoryItem(BaseModel):
    id: int
    file_name: str
    template_type: str
    total_rows: int
    inserted_count: int
    updated_count: int
    duplicate_count: int
    failed_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
