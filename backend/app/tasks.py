from __future__ import annotations

import asyncio
import re
import uuid
from pathlib import Path

import docx
import fitz
import tiktoken
from celery import Celery
from openai import OpenAI
from sqlalchemy import delete, select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.knowledge_base import KBChunk, KBDocument

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 100
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

celery_app = Celery("aria", broker=settings.REDIS_URL, backend=settings.REDIS_URL)


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def _clean_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    if not non_empty:
        return ""

    normalized = []
    for line in non_empty:
        if re.fullmatch(r"\d+", line):
            continue
        normalized.append(line)

    text = "\n".join(normalized)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_text(file_path: Path, file_type: str) -> str:
    if file_type == "pdf":
        with fitz.open(file_path) as doc:
            return "\n".join(page.get_text("text") for page in doc)
    if file_type == "docx":
        document = docx.Document(file_path)
        return "\n".join(paragraph.text for paragraph in document.paragraphs)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _chunk_text(text: str) -> list[tuple[int, str]]:
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(text)
    if not tokens:
        return []

    chunks: list[tuple[int, str]] = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for chunk_index, start in enumerate(range(0, len(tokens), step)):
        chunk_tokens = tokens[start : start + CHUNK_SIZE]
        chunk_text = encoder.decode(chunk_tokens).strip()
        if chunk_text:
            chunks.append((chunk_index, chunk_text))
    return chunks


def _embed_chunks(chunks: list[tuple[int, str]]) -> list[tuple[int, str, str]]:
    if not chunks:
        return []
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for document embeddings")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    embedded: list[tuple[int, str, str]] = []
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start : start + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[content for _, content in batch],
        )
        for (chunk_index, content), embedding_data in zip(batch, response.data, strict=True):
            embedded.append((chunk_index, content, _vector_literal(embedding_data.embedding)))
    return embedded


async def _process_document_async(document_id: uuid.UUID) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(KBDocument).where(KBDocument.id == document_id))
        document = result.scalar_one_or_none()
        if document is None:
            return

        document.status = "processing"
        document.error_message = None
        document.chunk_count = 0
        await db.flush()

        try:
            file_path = Path(document.file_path)
            raw_text = _extract_text(file_path, document.file_type)
            clean_text = _clean_text(raw_text)
            if not clean_text:
                raise ValueError("No extractable text was found in the uploaded document")

            chunks = _chunk_text(clean_text)
            if not chunks:
                raise ValueError("Document content was too short to chunk")

            embedded_chunks = _embed_chunks(chunks)

            await db.execute(delete(KBChunk).where(KBChunk.document_id == document.id))
            db.add_all(
                [
                    KBChunk(
                        document_id=document.id,
                        tenant_id=document.tenant_id,
                        content=content,
                        embedding=embedding,
                        chunk_index=chunk_index,
                        metadata_={
                            "filename": document.filename,
                            "file_type": document.file_type,
                            "department_tag": document.department_tag,
                        },
                    )
                    for chunk_index, content, embedding in embedded_chunks
                ]
            )

            document.chunk_count = len(embedded_chunks)
            document.status = "ready"
            document.error_message = None
            await db.commit()
        except Exception as exc:
            document.status = "error"
            document.error_message = str(exc)
            await db.commit()
            raise


@celery_app.task(name="app.tasks.process_document")
def process_document(document_id: str) -> None:
    asyncio.run(_process_document_async(uuid.UUID(document_id)))
