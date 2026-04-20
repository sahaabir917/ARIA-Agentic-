"""
Supabase JWT authentication middleware.

Decodes the Bearer token from the Authorization header, validates it against
SUPABASE_JWT_SECRET (HS256), looks up the User + Tenant in our DB, and
attaches them to request.state so dependencies can read them without an extra
DB round-trip.
"""
from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.user import User

logger = structlog.get_logger()

# Routes that do NOT require authentication
PUBLIC_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/signup",
    "/auth/login",
    "/auth/dev-login",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request.state.current_user = None
        request.state.current_tenant = None

        # Let CORS preflight pass through so CORSMiddleware can handle it
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS or request.url.path.startswith("/docs"):
            return await call_next(request)

        authorization: str | None = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = authorization.removeprefix("Bearer ").strip()

        try:
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        except JWTError as exc:
            logger.warning("jwt_decode_failed", error=str(exc))
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
            )

        supabase_uid: str | None = payload.get("sub")
        if not supabase_uid:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token missing subject claim"},
            )

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(User)
                .options(selectinload(User.tenant))
                .where(User.supabase_uid == supabase_uid)
            )
            user = result.scalar_one_or_none()

        if user is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "User not found — please complete signup"},
            )

        request.state.current_user = user
        request.state.current_tenant = user.tenant
        return await call_next(request)
