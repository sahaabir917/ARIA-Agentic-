import uuid

from pydantic import BaseModel, EmailStr

from app.schemas.tenant import TenantRead
from app.schemas.user import UserRead


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str | None = None
    company_name: str
    supabase_uid: str
    password: str | None = None  # dev-mode only; ignored when Supabase is configured


class SetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str
    bootstrap_key: str  # must equal DEV_LOGIN_PASSWORD to bootstrap existing accounts


class LoginRequest(BaseModel):
    token: str


class DevLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user: UserRead
    tenant: TenantRead
    token: str | None = None
