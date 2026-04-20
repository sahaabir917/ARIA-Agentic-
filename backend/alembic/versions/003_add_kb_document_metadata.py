"""add_kb_document_metadata

Revision ID: 003
Revises: 002
Create Date: 2026-04-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("kb_documents", sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"))
    op.add_column("kb_documents", sa.Column("uploaded_by_user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key(
        "fk_kb_documents_uploaded_by_user_id_users",
        "kb_documents",
        "users",
        ["uploaded_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_kb_documents_uploaded_by_user_id", "kb_documents", ["uploaded_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_kb_documents_uploaded_by_user_id", table_name="kb_documents")
    op.drop_constraint("fk_kb_documents_uploaded_by_user_id_users", "kb_documents", type_="foreignkey")
    op.drop_column("kb_documents", "uploaded_by_user_id")
    op.drop_column("kb_documents", "file_size")
