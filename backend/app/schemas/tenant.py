import uuid
from datetime import datetime

from pydantic import BaseModel


class TenantRead(BaseModel):
    id: uuid.UUID
    name: str
    industry: str | None
    description: str | None
    settings: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantCreate(BaseModel):
    name: str
    industry: str | None = None
    description: str | None = None
    settings: dict = {}


class TenantUpdate(BaseModel):
    name: str | None = None
    industry: str | None = None
    description: str | None = None
    settings: dict | None = None
