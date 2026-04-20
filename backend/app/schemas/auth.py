import uuid

from pydantic import BaseModel, EmailStr

from app.schemas.tenant import TenantRead
from app.schemas.user import UserRead


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str | None = None
    company_name: str
    supabase_uid: str


class LoginRequest(BaseModel):
    token: str


class DevLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: UserRead
    tenant: TenantRead
    token: str | None = None
