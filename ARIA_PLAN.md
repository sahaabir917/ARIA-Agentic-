# ARIA Application — Full Build Plan

## What Is ARIA

ARIA is a company-specific AI evaluation platform. When a business idea is submitted, it passes through an orchestrator (policy/values check), then fans out to seven specialized department agents (Marketing, Sales, Development, Design, HR, Finance, Market Research), each reasoning against the company's uploaded knowledge base. Agents then enter a structured multi-round discussion, conflicts are detected and categorized, and the system produces a final comprehensive report with feasibility scores, cost breakdown, conflict registry, and a proceed/modify/pause/abandon recommendation.

---

## Current State

The backend scaffold already exists:
- FastAPI app, all SQLAlchemy models, `pyproject.toml`, `config.py`, `database.py`, Alembic setup
- API route stubs registered in `main.py` but not yet implemented
- No Alembic migration created yet
- No frontend exists

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn (async) |
| Database | PostgreSQL + pgvector (1536-dim) |
| ORM / Migrations | SQLAlchemy 2.0 async + Alembic |
| Task Queue | Celery + Redis |
| AI Agents | Anthropic Claude (Opus 4.6 orchestrator, Sonnet 4.6 specialists) |
| Embeddings | OpenAI `text-embedding-3-small` |
| RAG | LlamaIndex + pgvector store |
| Market Research | Tavily API |
| Auth | Supabase JWT |
| PDF Export | WeasyPrint |
| Frontend | Next.js 14 (App Router) + Tailwind CSS + shadcn/ui |
| Real-time | Server-Sent Events (SSE) via `/stream` route |

---

## Target Directory Structure

```
ARIA/
├── .env.example
├── docker-compose.yml
├── frontend/
│   ├── package.json
│   └── app/
│       ├── (auth)/login/
│       ├── dashboard/
│       ├── knowledge-base/
│       ├── evaluations/
│       │   ├── new/
│       │   └── [id]/
│       └── settings/
└── backend/
    ├── alembic/versions/          ← migrations
    └── app/
        ├── main.py                (exists)
        ├── config.py              (exists)
        ├── database.py            (exists)
        ├── models/                (exists — complete)
        ├── schemas/               ← NEW: Pydantic request/response models
        ├── api/                   ← NEW: route implementations
        │   ├── auth.py
        │   ├── tenants.py
        │   ├── users.py
        │   ├── knowledge_base.py
        │   ├── evaluations.py
        │   └── stream.py
        ├── services/              ← NEW: business logic
        │   ├── auth_service.py
        │   ├── kb_service.py
        │   └── evaluation_service.py
        ├── agents/                ← NEW: AI agent system
        │   ├── base.py
        │   ├── orchestrator.py
        │   ├── department/
        │   │   ├── marketing.py
        │   │   ├── sales.py
        │   │   ├── development.py
        │   │   ├── design.py
        │   │   ├── hr.py
        │   │   └── finance.py
        │   ├── market_research.py
        │   ├── discussion.py
        │   ├── conflict_detector.py
        │   └── synthesizer.py
        └── tasks/                 ← NEW: Celery async tasks
            ├── celery_app.py
            ├── kb_tasks.py
            └── evaluation_tasks.py
```

---

## Build Phases

### Phase 1 — Database & Infrastructure

1. Generate initial Alembic migration from existing models → `alembic revision --autogenerate -m "initial"` → `alembic upgrade head`
2. Write `backend/scripts/seed.py` — creates demo tenant + admin user for local dev
3. Write `docker-compose.yml` with services: `postgres` (pgvector), `redis`, `backend`, `celery_worker`

---

### Phase 2 — Pydantic Schemas

Create `backend/app/schemas/` with request/response models for every entity:

- `AuthSchemas` — `LoginRequest`, `TokenResponse`, `UserMe`
- `TenantSchemas` — `TenantCreate`, `TenantRead`, `TenantUpdate`
- `KBSchemas` — `DocumentUploadResponse`, `DocumentRead`, `DocumentList`
- `EvaluationSchemas` — `EvaluationCreate`, `EvaluationRead`, `EvaluationStatus`, `EvaluationReport`
- `AgentSchemas` — `AgentRunRead`, `DiscussionRoundRead`, `ConflictRead`

---

### Phase 3 — Auth & Multi-Tenancy

**Files:** `api/auth.py`, `api/tenants.py`, `api/users.py`, `services/auth_service.py`

1. **Supabase JWT middleware** — decode JWT from `Authorization: Bearer`, resolve tenant from `tenant_id`, attach to `request.state`
2. **RBAC dependencies** — `require_admin`, `require_analyst`, `require_any_role` as FastAPI `Depends()`
3. **Routes:**
   - `POST /auth/login` — exchange credentials for JWT
   - `GET /auth/me` — current user + tenant
   - `GET /tenants/{id}` — tenant details (admin only)
   - `PATCH /tenants/{id}` — update settings JSONB
   - `GET /users` — list users in tenant
   - `POST /users/invite` — create user record
   - `PATCH /users/{id}/role` — change role

---

### Phase 4 — Knowledge Base Pipeline

**Files:** `api/knowledge_base.py`, `services/kb_service.py`, `tasks/kb_tasks.py`

**Upload flow:**
1. `POST /knowledge-base/upload` — accept multipart file (PDF/DOCX/TXT, max 50MB), save to storage, create `KBDocument` record with status `pending`, enqueue Celery task
2. `GET /knowledge-base` — paginated document list for tenant
3. `DELETE /knowledge-base/{id}` — delete document + all chunks

**Celery task `process_document`:**
1. Extract text: PyMuPDF (PDF), python-docx (DOCX), plain read (TXT)
2. Chunk: 512-token chunks, 50-token overlap
3. Embed via OpenAI `text-embedding-3-small`
4. Store in `kb_chunk` table with pgvector embedding
5. Update document status to `ready` or `error`

**RAG query helper** (`kb_service.retrieve`):
- Input: `tenant_id` + `query_text` + optional `department` filter
- Embed query → cosine-similarity search via pgvector → return top-k chunks as context string

---

### Phase 5 — Agent System

**Files:** `agents/`

#### BaseAgent (`base.py`)
- Holds: `agent_type`, `system_prompt`, `model`
- `async run(idea, context, prior_outputs) → AgentResult`
  1. Retrieve RAG context for this agent's department
  2. Build messages: system prompt + idea + kb_context + prior_outputs
  3. Call Anthropic Claude with **prompt caching** on system prompt block (`cache_control: {"type": "ephemeral"}`)
  4. Parse structured JSON response
  5. Return `AgentResult(structured_result, raw_output, tokens_used)`

#### Orchestrator (`orchestrator.py`)
- Model: `claude-opus-4-6`
- Checks idea against company policy docs in KB
- Returns: `{verdict: approved|rejected|conditional, reason, conditions}`
- If `rejected` → evaluation stops, no department agents run

#### Department Agents (`department/*.py`)
Seven agents with domain-specific system prompts. Each returns structured JSON:
```json
{
  "department": "marketing",
  "feasibility_score": 0-100,
  "analysis": "...",
  "key_concerns": [],
  "recommendations": [],
  "budget_estimate": {},
  "verdict": "proceed|modify|pause|abandon"
}
```

#### Market Research Agent (`market_research.py`)
- Searches via Tavily API: competitor landscape, industry trends, consumer demand, news
- Returns: `{market_size, demand_signals, competitor_count, trend_direction, market_score: 0-100}`

---

### Phase 6 — Multi-Agent Discussion & Conflict Detection

**Files:** `agents/discussion.py`, `agents/conflict_detector.py`

**Discussion (`discussion.py`):**
1. Collect all department agent outputs
2. Round 1 — each agent receives other agents' outputs and generates a reaction paragraph
3. Round 2 — surface top conflicts, ask relevant agents to propose resolutions
4. Maximum 3 rounds (cost/latency control)
5. Persist each round as `DiscussionRound` records

**Conflict detector (`conflict_detector.py`):**
- Input: all agent structured outputs
- Use Claude Sonnet to identify tensions: budget mismatch, timeline clash, resource overlap, strategic misalignment
- Categorize by `type` and `severity` (low / medium / high / critical)
- Generate 2-3 `resolution_scenarios` per conflict: `{title, description, tradeoffs}`
- Persist to `conflict` table

---

### Phase 7 — Synthesis & Report Generation

**File:** `agents/synthesizer.py`

1. Aggregate all agent results + discussion rounds + resolved conflicts
2. Call Claude Opus for executive summary + final recommendation
3. Calculate composite feasibility scores: overall = weighted average of (financial, market, technical, operational, strategic)
4. Assemble full `ReportData` dict
5. Render HTML report template → PDF via WeasyPrint
6. Store PDF path + JSON report in `report` table
7. Update evaluation status to `complete`

**Report sections:**
- Executive Summary
- Feasibility Scorecard (6 dimensions)
- Policy & Compliance Verdict
- Department-by-Department Analysis
- Market Research Findings
- Conflict Registry + Resolution Scenarios
- Cost Breakdown
- Final Recommendation + Confidence Score

---

### Phase 8 — Evaluation Orchestration

**Files:** `api/evaluations.py`, `services/evaluation_service.py`, `tasks/evaluation_tasks.py`

**API routes:**
- `POST /evaluations` — create evaluation, enqueue Celery task, return `{id, status: queued}`
- `GET /evaluations` — paginated list with status + scores
- `GET /evaluations/{id}` — full detail: agent runs, discussion, conflicts, report
- `GET /evaluations/{id}/report/pdf` — download PDF
- `DELETE /evaluations/{id}` — soft-delete

**Celery task `run_evaluation` pipeline:**
```
1. Policy check (Orchestrator)           → status: running
2. Fan out all 7 agents + market research in parallel (asyncio.gather)
3. Conflict detection
4. Multi-round discussion (2-3 rounds)
5. Synthesis + PDF report generation
6. status: complete → publish SSE event
```

All agent runs persisted to `agent_run` table with timing + token usage.

---

### Phase 9 — Real-Time Streaming (SSE)

**File:** `api/stream.py`

- `GET /stream/evaluations/{id}` — SSE endpoint
- Celery tasks publish to Redis pub/sub channel → SSE endpoint subscribes and forwards
- Events emitted:
  - `{event: "status_update", data: {stage: "policy_check"}}`
  - `{event: "agent_complete", data: {agent: "marketing", score: 72}}`
  - `{event: "conflict_detected", data: {count: 3}}`
  - `{event: "complete", data: {report_id: "..."}}`

---

### Phase 10 — Frontend (Next.js 14)

**Directory:** `frontend/`

| Route | Purpose |
|---|---|
| `/login` | Supabase Auth UI |
| `/dashboard` | Recent evaluations, stats, submit idea CTA |
| `/knowledge-base` | Upload documents, list with status badges, delete |
| `/evaluations/new` | Form: idea title + description |
| `/evaluations` | Table of all evaluations with status + scores |
| `/evaluations/[id]` | Live progress (SSE stepper) + final report viewer |
| `/settings` | Tenant settings, team management |

**Key components:**
- `EvaluationProgress` — SSE-driven stepper, each agent lights up as it completes
- `ReportViewer` — tabbed: scorecard, departments, conflicts, recommendation
- `FeasibilityRadar` — radar chart (Recharts) across 6 dimensions
- `ConflictCard` — expandable conflict with resolution scenarios
- `DocumentUploader` — drag-and-drop with processing status polling

**State:** React Query (server state) + Zustand (UI state)

---

### Phase 11 — Testing

- Unit tests per agent (mock Claude + RAG)
- Integration tests for KB ingestion pipeline (real Postgres, mocked embeddings)
- Integration tests for evaluation orchestration (mock Claude, real DB)
- API endpoint tests with `httpx.AsyncClient`
- Target: ≥ 80% coverage on `agents/` and `services/`

---

## Build Order

```
Phase 1  → Migrations + Docker Compose
Phase 2  → Pydantic Schemas
Phase 3  → Auth + Multi-Tenancy
Phase 4  → Knowledge Base Pipeline
Phase 5  → Agent System
Phase 6  → Discussion + Conflict Detection
Phase 7  → Synthesis + Reports
Phase 8  → Evaluation API + Celery Pipeline
Phase 9  → SSE Streaming
Phase 10 → Frontend
Phase 11 → Tests
```

---

## End-to-End Verification

1. `docker-compose up` — all services healthy (postgres, redis, backend, celery)
2. `POST /auth/login` → receive JWT
3. Upload a PDF → document status transitions `pending → processing → ready`
4. `POST /evaluations` with idea text → evaluation progresses through all stages → report PDF downloadable
5. Connect to `/stream/evaluations/{id}` during evaluation → receive SSE events in real time
6. Frontend: submit idea → watch live agent progress → view full report with radar chart + conflict registry
7. `pytest --cov=app` → ≥ 80% coverage
