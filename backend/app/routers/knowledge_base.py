from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.knowledge_base import KBDocument
from app.models.user import User

router = APIRouter()

# ─── Schemas ──────────────────────────────────────────────────────────────────

class KBHealthResponse(BaseModel):
    document_count: int
    chunk_count: int
    last_upload_date: str | None

# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("/health", response_model=KBHealthResponse)
async def kb_health(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    tid = current_user.tenant_id

    doc_r = await db.execute(
        select(func.count(KBDocument.id)).where(KBDocument.tenant_id == tid)
    )
    doc_count = doc_r.scalar_one() or 0

    chunk_r = await db.execute(
        select(func.coalesce(func.sum(KBDocument.chunk_count), 0)).where(KBDocument.tenant_id == tid)
    )
    chunk_count = int(chunk_r.scalar_one() or 0)

    last_r = await db.execute(
        select(func.max(KBDocument.created_at)).where(KBDocument.tenant_id == tid)
    )
    last_date = last_r.scalar_one()

    return KBHealthResponse(
        document_count=doc_count,
        chunk_count=chunk_count,
        last_upload_date=last_date.isoformat() if last_date else None,
    )
