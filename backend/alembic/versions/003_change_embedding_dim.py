"""change_embedding_dim_768

Revision ID: 003
Revises: 002
Create Date: 2026-04-20

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("SAVEPOINT pgvector_resize"))
    try:
        conn.execute(text(
            "ALTER TABLE kb_chunks ALTER COLUMN embedding TYPE vector(768) "
            "USING embedding::vector"
        ))
        conn.execute(text("DROP INDEX IF EXISTS kb_chunks_embedding_idx"))
        conn.execute(text(
            "CREATE INDEX ON kb_chunks USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100)"
        ))
        conn.execute(text("RELEASE SAVEPOINT pgvector_resize"))
    except Exception:
        conn.execute(text("ROLLBACK TO SAVEPOINT pgvector_resize"))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("SAVEPOINT pgvector_restore"))
    try:
        conn.execute(text(
            "ALTER TABLE kb_chunks ALTER COLUMN embedding TYPE vector(1536) "
            "USING embedding::vector"
        ))
        conn.execute(text("DROP INDEX IF EXISTS kb_chunks_embedding_idx"))
        conn.execute(text(
            "CREATE INDEX ON kb_chunks USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100)"
        ))
        conn.execute(text("RELEASE SAVEPOINT pgvector_restore"))
    except Exception:
        conn.execute(text("ROLLBACK TO SAVEPOINT pgvector_restore"))
