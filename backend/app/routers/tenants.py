"""
Tenant settings routes — scoped to the caller's own tenant.

GET   /tenants/{id}  — return tenant profile
PATCH /tenants/{id}  — update name, industry, description, settings
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.tenant import TenantRead, TenantUpdate
from app.services import tenant_service

router = APIRouter()


def _assert_own_tenant(tenant_id: uuid.UUID, current_user: User) -> None:
    if tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to another tenant is not allowed")


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    tenant_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    _assert_own_tenant(tenant_id, current_user)
    tenant = await tenant_service.get_tenant(db, tenant_id)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: uuid.UUID,
    body: TenantUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    _assert_own_tenant(tenant_id, current_user)
    tenant = await tenant_service.update_tenant(db, tenant_id, body)
    if tenant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    await db.commit()
    return tenant
