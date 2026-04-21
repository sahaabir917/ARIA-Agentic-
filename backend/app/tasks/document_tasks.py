from __future__ import annotations

import re
import uuid
from typing import Any

import fitz  # PyMuPDF
import docx
import tiktoken
import google.generativeai as genai
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.models.knowledge_base import KBChunk, KBDocument
from app.tasks.celery_app import celery_app

genai.configure(api_key=settings.GOOGLE_API_KEY)

_CHUNK_TOKENS = 512
_OVERLAP_TOKENS = 50
_EMBED_BATCH = 100
_EMBED_MODEL = "models/gemini-embedding-001"

# Sync engine for Celery (psycopg2 instead of asyncpg)
_sync_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
_sync_engine = create_engine(_sync_url, pool_pre_ping=True)
SyncSession = sessionmaker(bind=_sync_engine)


# ─── Text extraction ──────────────────────────────────────────────────────────

def _extract_pdf(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)


def _extract_docx(path: str) -> str:
    d = docx.Document(path)
    return "\n".join(p.text for p in d.paragraphs)


def _extract_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _extract_text(path: str, file_type: str) -> str:
    if file_type == "pdf":
        return _extract_pdf(path)
    if file_type == "docx":
        return _extract_docx(path)
    return _extract_txt(path)


# ─── Chunking ─────────────────────────────────────────────────────────────────

def _clean(text: str) -> str:
    return re.sub(r"\s{3,}", "\n\n", text).strip()


def _chunk(text: str) -> list[str]:
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    stride = _CHUNK_TOKENS - _OVERLAP_TOKENS
    chunks = []
    for i in range(0, len(tokens), stride):
        piece = tokens[i : i + _CHUNK_TOKENS]
        if piece:
            chunks.append(enc.decode(piece))
    return chunks


# ─── Embedding ────────────────────────────────────────────────────────────────

def _embed_batch(texts: list[str]) -> list[list[float]]:
    result = genai.embed_content(
        model=_EMBED_MODEL,
        content=texts,
        task_type="retrieval_document",
        output_dimensionality=768,
    )
    raw = result["embedding"]
    # Single string → list[float]; batch → list[list[float]]
    if raw and isinstance(raw[0], float):
        return [raw]
    return raw


def _embed_all(chunks: list[str]) -> list[list[float]]:
    embeddings: list[list[float]] = []
    for i in range(0, len(chunks), _EMBED_BATCH):
        batch = chunks[i : i + _EMBED_BATCH]
        embeddings.extend(_embed_batch(batch))
    return embeddings


# ─── Sync processing core ─────────────────────────────────────────────────────

def _set_status(db: Session, doc_id: uuid.UUID, status: str, **kwargs: Any) -> None:
    db.execute(
        update(KBDocument)
        .where(KBDocument.id == doc_id)
        .values(status=status, **kwargs)
    )
    db.commit()


def _process(document_id: str) -> None:
    doc_uuid = uuid.UUID(document_id)

    with SyncSession() as db:
        doc = db.execute(
            select(KBDocument).where(KBDocument.id == doc_uuid)
        ).scalar_one_or_none()
        if not doc:
            return

        try:
            _set_status(db, doc_uuid, "processing")

            raw = _extract_text(doc.file_path, doc.file_type)
            cleaned = _clean(raw)
            chunks = _chunk(cleaned)
            embeddings = _embed_all(chunks)

            chunk_rows = [
                KBChunk(
                    id=uuid.uuid4(),
                    document_id=doc_uuid,
                    tenant_id=doc.tenant_id,
                    content=chunk_text,
                    embedding=str(emb),
                    chunk_index=idx,
                    metadata_={"chunk_index": idx, "document_id": document_id},
                )
                for idx, (chunk_text, emb) in enumerate(zip(chunks, embeddings))
            ]
            db.add_all(chunk_rows)
            db.commit()

            _set_status(db, doc_uuid, "ready", chunk_count=len(chunks))

        except Exception as exc:
            _set_status(db, doc_uuid, "error", error_message=str(exc))
            raise


# ─── Celery task ──────────────────────────────────────────────────────────────

@celery_app.task(name="process_document", bind=True, max_retries=3)
def process_document(self: Any, document_id: str) -> None:
    try:
        _process(document_id)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
