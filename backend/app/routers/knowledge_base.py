from __future__ import annotations

import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.knowledge_base import KBDocument
from app.models.user import User
from app.schemas.knowledge_base import KBDepartmentUpdate, KBDocumentList, KBDocumentRead

router = APIRouter()

_ALLOWED_TYPES = {"pdf", "docx", "txt"}


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


@router.post("/upload", response_model=KBDocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
):
    # Validate file type
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '.{ext}'. Allowed: pdf, docx, txt",
        )

    # Read and validate size
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_SIZE_MB} MB limit",
        )

    # Save to disk
    tenant_dir = os.path.join(settings.UPLOAD_DIR, str(current_user.tenant_id))
    os.makedirs(tenant_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(tenant_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(content)

    # Create DB record
    doc = KBDocument(
        id=uuid.uuid4(),
        tenant_id=current_user.tenant_id,
        filename=file.filename,
        file_path=file_path,
        file_type=ext,
        status="pending",
        chunk_count=0,
        file_size=len(content),
        uploaded_by=current_user.full_name or current_user.email,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # Enqueue processing task (import here to avoid circular imports at module load)
    from app.tasks.document_tasks import process_document
    process_document.delay(str(doc.id))

    return KBDocumentRead(
        **{k: getattr(doc, k) for k in KBDocumentRead.model_fields if k != "sample_chunks"},
        sample_chunks=[],
    )


@router.get("", response_model=KBDocumentList)
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = select(KBDocument).where(KBDocument.tenant_id == current_user.tenant_id)
    if status_filter:
        q = q.where(KBDocument.status == status_filter)
    q = q.order_by(KBDocument.created_at.desc())

    count_r = await db.execute(
        select(func.count()).select_from(q.subquery())
    )
    total = count_r.scalar_one() or 0

    result = await db.execute(q.offset(offset).limit(limit))
    docs = result.scalars().all()

    return KBDocumentList(
        items=[
            KBDocumentRead(
                **{k: getattr(d, k) for k in KBDocumentRead.model_fields if k != "sample_chunks"},
                sample_chunks=[],
            )
            for d in docs
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KBDocument).where(
            KBDocument.id == doc_id,
            KBDocument.tenant_id == current_user.tenant_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Delete file from disk (ignore if already gone)
    try:
        os.remove(doc.file_path)
    except FileNotFoundError:
        pass

    await db.delete(doc)
    await db.commit()


@router.patch("/{doc_id}", response_model=KBDocumentRead)
async def update_department_tag(
    doc_id: uuid.UUID,
    body: KBDepartmentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(KBDocument).where(
            KBDocument.id == doc_id,
            KBDocument.tenant_id == current_user.tenant_id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    await db.execute(
        update(KBDocument)
        .where(KBDocument.id == doc_id)
        .values(department_tag=body.department_tag)
    )
    await db.commit()
    await db.refresh(doc)
    return KBDocumentRead(
        **{k: getattr(doc, k) for k in KBDocumentRead.model_fields if k != "sample_chunks"},
        sample_chunks=[],
    )
