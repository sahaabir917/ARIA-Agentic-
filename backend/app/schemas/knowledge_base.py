from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class KBDocumentRead(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: str
    file_size: int
    uploaded_by: str | None
    status: str
    chunk_count: int
    department_tag: str | None
    error_message: str | None
    created_at: datetime
    sample_chunks: list[str] = []

    model_config = {"from_attributes": True}


class KBDocumentList(BaseModel):
    items: list[KBDocumentRead]
    total: int
    limit: int
    offset: int


class KBDepartmentUpdate(BaseModel):
    department_tag: str | None = None
