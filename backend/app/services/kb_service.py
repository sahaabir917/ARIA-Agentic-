from __future__ import annotations

import uuid
from collections import defaultdict
from pathlib import Path

from openai import AsyncOpenAI
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.knowledge_base import KBChunk, KBDocument

EMBEDDING_MODEL = "text-embedding-3-small"


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def uploads_root() -> Path:
    root = Path(settings.UPLOAD_DIR)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root


async def get_health(db: AsyncSession, tenant_id: uuid.UUID) -> tuple[int, int, str | None]:
    doc_r = await db.execute(
        select(func.count(KBDocument.id)).where(KBDocument.tenant_id == tenant_id)
    )
    chunk_r = await db.execute(
        select(func.coalesce(func.sum(KBDocument.chunk_count), 0)).where(KBDocument.tenant_id == tenant_id)
    )
    last_r = await db.execute(
        select(func.max(KBDocument.created_at)).where(KBDocument.tenant_id == tenant_id)
    )

    last_date = last_r.scalar_one()
    return (
        int(doc_r.scalar_one() or 0),
        int(chunk_r.scalar_one() or 0),
        last_date.isoformat() if last_date else None,
    )


async def list_documents(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    status: str | None,
    limit: int,
    offset: int,
) -> tuple[list[KBDocument], int, dict[uuid.UUID, list[str]]]:
    filters = [KBDocument.tenant_id == tenant_id]
    if status:
        filters.append(KBDocument.status == status)

    total_r = await db.execute(select(func.count(KBDocument.id)).where(*filters))
    docs_r = await db.execute(
        select(KBDocument)
        .options(selectinload(KBDocument.uploaded_by))
        .where(*filters)
        .order_by(KBDocument.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    documents = list(docs_r.scalars().all())
    samples = await get_sample_chunks(db, [doc.id for doc in documents])
    return documents, int(total_r.scalar_one() or 0), samples


async def get_document_for_tenant(
    db: AsyncSession,
    document_id: uuid.UUID,
    tenant_id: uuid.UUID,
) -> KBDocument | None:
    result = await db.execute(
        select(KBDocument)
        .options(selectinload(KBDocument.uploaded_by))
        .where(KBDocument.id == document_id, KBDocument.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def get_sample_chunks(
    db: AsyncSession,
    document_ids: list[uuid.UUID],
) -> dict[uuid.UUID, list[str]]:
    if not document_ids:
        return {}

    result = await db.execute(
        select(KBChunk.document_id, KBChunk.content)
        .where(KBChunk.document_id.in_(document_ids))
        .order_by(KBChunk.document_id, KBChunk.chunk_index)
    )

    grouped: dict[uuid.UUID, list[str]] = defaultdict(list)
    for document_id, content in result.all():
        if len(grouped[document_id]) < 3:
            grouped[document_id].append(content)
    return grouped


async def retrieve(
    tenant_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    department: str | None = None,
) -> str:
    if not settings.OPENAI_API_KEY:
        return ""

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    embedding_response = await client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
    )
    embedding = _vector_literal(embedding_response.data[0].embedding)

    similarity_sql = text(
        """
        SELECT
            c.content,
            c.chunk_index,
            d.filename,
            d.department_tag
        FROM kb_chunks AS c
        JOIN kb_documents AS d ON d.id = c.document_id
        WHERE c.tenant_id = :tenant_id
          AND d.status = 'ready'
          AND (:department IS NULL OR d.department_tag = :department OR d.department_tag IS NULL)
          AND c.embedding IS NOT NULL
        ORDER BY c.embedding <=> CAST(:embedding AS vector)
        LIMIT :top_k
        """
    )

    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            similarity_sql,
            {
                "tenant_id": tenant_id,
                "department": department,
                "embedding": embedding,
                "top_k": top_k,
            },
        )
        rows = result.mappings().all()

    if not rows:
        return ""

    parts = []
    for index, row in enumerate(rows, start=1):
        dept = row["department_tag"] or "all"
        parts.append(
            f"[{index}] {row['filename']} (chunk {row['chunk_index']}, department: {dept})\n{row['content']}"
        )
    return "\n\n".join(parts)
