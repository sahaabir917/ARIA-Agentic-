from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.knowledge_base import KBDocument
from app.models.user import User
from app.schemas.knowledge_base import (
    KBDocumentDeleteResponse,
    KBDocumentDepartmentUpdate,
    KBDocumentListResponse,
    KBDocumentRead,
    KBHealthResponse,
)
from app.services import kb_service
from app.tasks import process_document

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def _serialize_document(document: KBDocument, sample_chunks: list[str] | None = None) -> KBDocumentRead:
    uploader_name = (
        (document.uploaded_by.full_name or document.uploaded_by.email)
        if document.uploaded_by
        else "Unknown"
    )
    return KBDocumentRead(
        id=document.id,
        filename=document.filename,
        file_type=document.file_type,
        file_size=document.file_size,
        uploaded_by=uploader_name,
        created_at=document.created_at,
        status=document.status,
        chunk_count=document.chunk_count,
        department_tag=document.department_tag,
        error_message=document.error_message,
        sample_chunks=sample_chunks or [],
    )


@router.post("/upload", response_model=KBDocumentRead, status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF, DOCX, and TXT files are supported",
        )

    content = await file.read()
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit",
        )

    tenant_dir = kb_service.uploads_root() / str(current_user.tenant_id)
    tenant_dir.mkdir(parents=True, exist_ok=True)

    document_id = uuid.uuid4()
    stored_name = f"{document_id}_{Path(file.filename or 'document').name}"
    file_path = tenant_dir / stored_name
    file_path.write_bytes(content)

    document = KBDocument(
        id=document_id,
        tenant_id=current_user.tenant_id,
        filename=file.filename or stored_name,
        file_path=str(file_path),
        file_type=extension,
        file_size=len(content),
        uploaded_by_user_id=current_user.id,
        status="pending",
    )
    document.uploaded_by = current_user
    db.add(document)
    await db.flush()
    await db.refresh(document)
    document.uploaded_by = current_user

    try:
        process_document.delay(str(document.id))
    except Exception as exc:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document upload succeeded, but processing could not be queued",
        ) from exc

    return _serialize_document(document)


@router.get("", response_model=KBDocumentListResponse)
async def list_documents(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    documents, total, samples = await kb_service.list_documents(
        db,
        current_user.tenant_id,
        status=status,
        limit=limit,
        offset=offset,
    )
    return KBDocumentListResponse(
        items=[_serialize_document(document, samples.get(document.id)) for document in documents],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.patch("/{document_id}", response_model=KBDocumentRead)
async def update_document_department(
    document_id: uuid.UUID,
    body: KBDocumentDepartmentUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    document = await kb_service.get_document_for_tenant(db, document_id, current_user.tenant_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    document.department_tag = body.department
    await db.flush()

    samples = await kb_service.get_sample_chunks(db, [document.id])
    return _serialize_document(document, samples.get(document.id))


@router.delete("/{document_id}", response_model=KBDocumentDeleteResponse)
async def delete_document(
    document_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    document = await kb_service.get_document_for_tenant(db, document_id, current_user.tenant_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    await db.delete(document)
    return KBDocumentDeleteResponse(id=document_id)


@router.get("/health", response_model=KBHealthResponse)
async def kb_health(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    doc_count, chunk_count, last_date = await kb_service.get_health(db, current_user.tenant_id)
    return KBHealthResponse(
        document_count=doc_count,
        chunk_count=chunk_count,
        last_upload_date=last_date,
    )
