import uuid

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserInvite


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def create_user(db: AsyncSession, tenant_id: uuid.UUID, data: UserCreate) -> User:
    user = User(
        tenant_id=tenant_id,
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        supabase_uid=data.supabase_uid,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user_by_supabase_uid(db: AsyncSession, uid: str) -> User | None:
    result = await db.execute(select(User).where(User.supabase_uid == uid))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, tenant_id: uuid.UUID) -> list[User]:
    result = await db.execute(
        select(User).where(User.tenant_id == tenant_id).order_by(User.created_at)
    )
    return list(result.scalars().all())


async def invite_user(db: AsyncSession, tenant_id: uuid.UUID, data: UserInvite) -> User:
    user = User(
        tenant_id=tenant_id,
        email=data.email,
        full_name=data.full_name,
        role=data.role,
        supabase_uid=None,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_role(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID, role: str) -> User | None:
    user = await get_user_by_id(db, user_id, tenant_id)
    if user is None:
        return None
    user.role = role
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID) -> bool:
    user = await get_user_by_id(db, user_id, tenant_id)
    if user is None:
        return False
    await db.delete(user)
    await db.flush()
    return True
