"""
Seed script — creates two tenants (GreenTech Innovations + Heritage Financial Group)
with admin users and placeholder document records.

Usage:
    cd backend
    python -m scripts.seed
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models.tenant import Tenant
from app.models.user import User
from app.models.knowledge_base import KBDocument

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

GREENTECH_ID = uuid.UUID("aaaaaaaa-0000-0000-0000-000000000001")
HERITAGE_ID = uuid.UUID("bbbbbbbb-0000-0000-0000-000000000002")

GREENTECH_USER_ID = uuid.UUID("aaaaaaaa-0000-0000-0001-000000000001")
HERITAGE_USER_ID = uuid.UUID("bbbbbbbb-0000-0000-0001-000000000002")


GREENTECH_DOCS = [
    ("greentech_sustainability_charter.pdf", "pdf"),
    ("greentech_rd_budget_2025.pdf", "pdf"),
    ("greentech_team_structure.docx", "docx"),
    ("greentech_growth_strategy.docx", "docx"),
    ("greentech_brand_guide.pdf", "pdf"),
]

HERITAGE_DOCS = [
    ("heritage_risk_policy.pdf", "pdf"),
    ("heritage_compliance_guide.pdf", "pdf"),
    ("heritage_it_budget_2025.docx", "docx"),
    ("heritage_brand_guide.pdf", "pdf"),
    ("heritage_team_org.docx", "docx"),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # GreenTech Innovations
        greentech = Tenant(
            id=GREENTECH_ID,
            name="GreenTech Innovations",
            industry="Clean Technology",
            description="Mid-size sustainable technology company focused on clean energy solutions.",
            settings={},
        )
        db.add(greentech)

        greentech_admin = User(
            id=GREENTECH_USER_ID,
            tenant_id=GREENTECH_ID,
            email="admin@greentech.example.com",
            full_name="GreenTech Admin",
            role="admin",
            supabase_uid=None,
        )
        db.add(greentech_admin)

        for filename, ftype in GREENTECH_DOCS:
            db.add(KBDocument(
                tenant_id=GREENTECH_ID,
                filename=filename,
                file_path=f"uploads/{GREENTECH_ID}/{filename}",
                file_type=ftype,
                status="pending",
                chunk_count=0,
            ))

        # Heritage Financial Group
        heritage = Tenant(
            id=HERITAGE_ID,
            name="Heritage Financial Group",
            industry="Banking & Finance",
            description="Conservative regional bank with strict regulatory compliance requirements.",
            settings={},
        )
        db.add(heritage)

        heritage_admin = User(
            id=HERITAGE_USER_ID,
            tenant_id=HERITAGE_ID,
            email="admin@heritage.example.com",
            full_name="Heritage Admin",
            role="admin",
            supabase_uid=None,
        )
        db.add(heritage_admin)

        for filename, ftype in HERITAGE_DOCS:
            db.add(KBDocument(
                tenant_id=HERITAGE_ID,
                filename=filename,
                file_path=f"uploads/{HERITAGE_ID}/{filename}",
                file_type=ftype,
                status="pending",
                chunk_count=0,
            ))

        await db.commit()
        print("Seed complete.")
        print(f"  GreenTech tenant id : {GREENTECH_ID}")
        print(f"  Heritage tenant id  : {HERITAGE_ID}")


if __name__ == "__main__":
    asyncio.run(seed())
