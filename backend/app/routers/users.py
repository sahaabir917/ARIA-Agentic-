"""
User management routes — all scoped to the caller's tenant.

GET    /users               — list all users in tenant (admin only)
POST   /users/invite        — invite a new user by email (admin only)
PATCH  /users/{id}/role     — change a user's role (admin only)
DELETE /users/{id}          — remove user from tenant (admin only)
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.schemas.user import UserInvite, UserRead, UserRoleUpdate
from app.services import user_service

router = APIRouter()

VALID_ROLES = {"admin", "analyst", "viewer"}


@router.get("", response_model=list[UserRead])
async def list_users(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    return await user_service.list_users(db, current_user.tenant_id)


@router.post("/invite", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def invite_user(
    body: UserInvite,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Role must be one of {VALID_ROLES}")
    user = await user_service.invite_user(db, current_user.tenant_id, body)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}/role", response_model=UserRead)
async def change_role(
    user_id: uuid.UUID,
    body: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Role must be one of {VALID_ROLES}")
    # Prevent admin from demoting themselves
    if user_id == current_user.id and body.role != "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")
    user = await user_service.update_role(db, user_id, current_user.tenant_id, body.role)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.commit()
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself")
    deleted = await user_service.delete_user(db, user_id, current_user.tenant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await db.commit()
