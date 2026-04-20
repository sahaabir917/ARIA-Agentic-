import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    full_name: str | None
    role: str
    supabase_uid: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: str = "analyst"
    supabase_uid: str | None = None


class UserInvite(BaseModel):
    email: EmailStr
    full_name: str | None = None
    role: str = "analyst"


class UserRoleUpdate(BaseModel):
    role: str
