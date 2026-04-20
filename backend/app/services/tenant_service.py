import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tenant import Tenant
from app.schemas.tenant import TenantCreate, TenantUpdate


async def create_tenant(db: AsyncSession, data: TenantCreate) -> Tenant:
    tenant = Tenant(
        name=data.name,
        industry=data.industry,
        description=data.description,
        settings=data.settings,
    )
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)
    return tenant


async def get_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def update_tenant(db: AsyncSession, tenant_id: uuid.UUID, data: TenantUpdate) -> Tenant | None:
    tenant = await get_tenant(db, tenant_id)
    if tenant is None:
        return None
    if data.name is not None:
        tenant.name = data.name
    if data.industry is not None:
        tenant.industry = data.industry
    if data.description is not None:
        tenant.description = data.description
    if data.settings is not None:
        tenant.settings = data.settings
    await db.flush()
    await db.refresh(tenant)
    return tenant
