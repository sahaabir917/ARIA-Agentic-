"""add_file_size_uploaded_by

Revision ID: 003
Revises: 002
Create Date: 2026-04-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("kb_documents", sa.Column("file_size", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("kb_documents", sa.Column("uploaded_by", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("kb_documents", "uploaded_by")
    op.drop_column("kb_documents", "file_size")
