"""
Auth routes — public endpoints (no JWT required) plus /auth/me (JWT required).

POST /auth/signup    — called by frontend after Supabase signUp() succeeds.
POST /auth/login     — validates a Supabase JWT and returns user + tenant from DB.
POST /auth/dev-login — dev-mode only: accepts email + any password, issues a signed JWT.
GET  /auth/me        — decodes JWT from middleware, returns current user + tenant.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import AuthResponse, DevLoginRequest, LoginRequest, SetPasswordRequest, SignupRequest
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate
from app.services import tenant_service, user_service

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    # Prevent duplicate signups
    existing = await user_service.get_user_by_supabase_uid(db, body.supabase_uid)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    tenant = await tenant_service.create_tenant(
        db, TenantCreate(name=body.company_name)
    )
    user = await user_service.create_user(
        db,
        tenant.id,
        UserCreate(
            email=body.email,
            full_name=body.full_name,
            role="admin",
            supabase_uid=body.supabase_uid,
        ),
    )
    if body.password:
        user.password_hash = user_service.hash_password(body.password)
    await db.commit()
    await db.refresh(user)
    await db.refresh(tenant)
    return AuthResponse(user=user, tenant=tenant)


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(
            body.token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    supabase_uid: str | None = payload.get("sub")
    if not supabase_uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing subject")

    user = await user_service.get_user_by_supabase_uid(db, supabase_uid)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found — please sign up first")

    tenant = await tenant_service.get_tenant(db, user.tenant_id)
    return AuthResponse(user=user, tenant=tenant)


@router.post("/dev-login", response_model=AuthResponse)
async def dev_login(body: DevLoginRequest, db: AsyncSession = Depends(get_db)):
    """Dev-mode login: validates email + per-user bcrypt password, issues a signed JWT."""
    user = await user_service.get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No account found for this email. Please sign up first.",
        )

    if not user.password_hash or not user_service.verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password.",
        )

    # Ensure the user has a supabase_uid so the auth middleware can look them up
    if user.supabase_uid is None:
        user.supabase_uid = str(user.id)
        await db.commit()
        await db.refresh(user)

    secret = settings.SUPABASE_JWT_SECRET or "dev-secret-placeholder"
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": user.supabase_uid, "iat": now, "exp": now + timedelta(days=7)},
        secret,
        algorithm="HS256",
    )

    tenant = await tenant_service.get_tenant(db, user.tenant_id)
    return AuthResponse(user=user, tenant=tenant, token=token)


@router.post("/set-password", status_code=status.HTTP_204_NO_CONTENT)
async def set_password(body: SetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Bootstrap endpoint: lets existing users set their own password using the shared dev key."""
    if body.bootstrap_key != settings.DEV_LOGIN_PASSWORD:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bootstrap key.")

    user = await user_service.get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No account found for this email.")

    user.password_hash = user_service.hash_password(body.new_password)
    await db.commit()


@router.get("/me", response_model=AuthResponse)
async def me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    tenant = await tenant_service.get_tenant(db, current_user.tenant_id)
    return AuthResponse(user=current_user, tenant=tenant)
