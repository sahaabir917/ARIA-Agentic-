import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class KBHealthResponse(BaseModel):
    document_count: int
    chunk_count: int
    last_upload_date: str | None


class KBDocumentRead(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    uploaded_by: str
    created_at: datetime
    status: str
    chunk_count: int
    department_tag: str | None
    error_message: str | None
    sample_chunks: list[str] = Field(default_factory=list)


class KBDocumentListResponse(BaseModel):
    items: list[KBDocumentRead]
    total: int
    limit: int
    offset: int


class KBDocumentDepartmentUpdate(BaseModel):
    department: str | None = None


class KBDocumentDeleteResponse(BaseModel):
    id: uuid.UUID
    deleted: bool = True
