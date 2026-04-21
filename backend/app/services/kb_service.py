from __future__ import annotations

import uuid

import google.generativeai as genai
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

_EMBED_MODEL = "models/gemini-embedding-001"


def embed_query(query: str) -> list[float]:
    result = genai.embed_content(
        model=_EMBED_MODEL,
        content=query,
        task_type="retrieval_query",
        output_dimensionality=768,
    )
    return result["embedding"]


async def retrieve(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    department: str | None = None,
) -> str:
    vector = embed_query(query)
    vector_str = str(vector)

    dept_filter = ""
    params: dict = {"tid": str(tenant_id), "vec": vector_str, "k": top_k}
    if department:
        dept_filter = (
            "AND kbc.document_id IN ("
            "  SELECT id FROM kb_documents WHERE tenant_id = :tid AND department_tag = :dept"
            ")"
        )
        params["dept"] = department

    sql = text(f"""
        SELECT kbc.content
        FROM kb_chunks kbc
        WHERE kbc.tenant_id = :tid
        {dept_filter}
        ORDER BY kbc.embedding <=> CAST(:vec AS vector)
        LIMIT :k
    """)

    result = await db.execute(sql, params)
    rows = result.fetchall()
    if not rows:
        return ""
    return "\n\n---\n\n".join(r[0] for r in rows)
