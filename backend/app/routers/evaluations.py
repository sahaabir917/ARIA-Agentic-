from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.evaluation import Evaluation
from app.models.user import User

router = APIRouter()

# ─── Schemas ──────────────────────────────────────────────────────────────────

class EvaluationItem(BaseModel):
    id: str
    title: str
    status: str
    outcome: str
    score: int | None
    created_at: str

class EvalStats(BaseModel):
    total: int
    total_trend: int
    passed: int
    passed_trend: int
    failed: int
    failed_trend: int

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _derive_outcome(status: str, policy_verdict: str | None, confidence: float | None) -> str:
    if status == "failed" or policy_verdict == "rejected":
        return "fail"
    if status in ("queued", "running"):
        return "pending"
    if status == "conditional" or policy_verdict == "conditional":
        return "warn"
    if status == "complete":
        if confidence is not None:
            if confidence >= 70:
                return "pass"
            if confidence >= 50:
                return "warn"
            return "fail"
        if policy_verdict == "approved":
            return "pass"
    return "pending"

# ─── Routes ───────────────────────────────────────────────────────────────────

@router.get("", response_model=list[EvaluationItem])
async def list_evaluations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
):
    result = await db.execute(
        select(Evaluation)
        .options(selectinload(Evaluation.report))
        .where(Evaluation.tenant_id == current_user.tenant_id)
        .order_by(Evaluation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    evals = result.scalars().all()

    items = []
    for ev in evals:
        confidence: float | None = None
        score: int | None = None
        if ev.report:
            confidence = ev.report.confidence_score
            score = round(confidence * 100) if confidence else None

        items.append(EvaluationItem(
            id=str(ev.id),
            title=ev.title,
            status=ev.status,
            outcome=_derive_outcome(ev.status, ev.policy_verdict, confidence),
            score=score,
            created_at=ev.created_at.isoformat(),
        ))
    return items


@router.get("/stats", response_model=EvalStats)
async def get_eval_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    tid = current_user.tenant_id

    async def count(stmt) -> int:
        r = await db.execute(stmt)
        return r.scalar_one() or 0

    total        = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid))
    total_trend  = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid, Evaluation.created_at >= week_ago))
    passed       = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid, Evaluation.policy_verdict == "approved"))
    passed_trend = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid, Evaluation.policy_verdict == "approved", Evaluation.created_at >= week_ago))
    failed       = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid, or_(Evaluation.status == "failed", Evaluation.policy_verdict == "rejected")))
    failed_trend = await count(select(func.count(Evaluation.id)).where(Evaluation.tenant_id == tid, or_(Evaluation.status == "failed", Evaluation.policy_verdict == "rejected"), Evaluation.created_at >= week_ago))

    return EvalStats(
        total=total, total_trend=total_trend,
        passed=passed, passed_trend=passed_trend,
        failed=failed, failed_trend=failed_trend,
    )
