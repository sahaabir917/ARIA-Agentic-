# ARIA — Full Application Build Plan

> **Stack:** CrewAI · Claude / GPT-4o / Gemini · FastAPI · PostgreSQL + pgvector · Next.js 14 · Tailwind CSS · Supabase Auth · Redis · Celery

---

## Overview

ARIA evaluates any incoming business idea through the eyes of your entire organization. Companies upload their internal documents to build a Knowledge Base. When an idea is submitted, a pipeline of AI agents — each powered by a different LLM — analyzes it from every department's perspective, discusses conflicts between their findings, and generates a single comprehensive report with a final recommendation.

This plan is divided into **25 segments**, starting from UI design and moving through backend, agents, sample data, and deployment.

---

## Multi-LLM Assignment (CrewAI)

Each CrewAI agent is assigned a specific LLM based on their role:

| Agent                       | LLM                        | Reason                                     |
| --------------------------- | -------------------------- | ------------------------------------------ |
| Orchestrator (policy check) | Claude Opus 4.6            | Highest reasoning for values alignment     |
| Marketing Agent             | GPT-4o                     | Strong at consumer insight and narrative   |
| Sales Agent                 | GPT-4o                     | Strong at opportunity framing              |
| Development Agent           | Claude Sonnet 4.6          | Technical depth and code-aware thinking    |
| Design Agent                | Gemini 1.5 Pro             | Visual and UX reasoning                    |
| HR Agent                    | Gemini 1.5 Pro             | People, culture, compliance reasoning      |
| Finance Agent               | GPT-4o                     | Numerical analysis and risk modeling       |
| Market Research Agent       | Claude Sonnet 4.6 + Tavily | External data + analytical synthesis       |
| Synthesizer (final report)  | Claude Opus 4.6            | Executive-level summary and recommendation |

---

## Sample Company Scenarios

### Scenario A — GreenTech Innovations (PASSES ✅)

- **Company type:** Mid-size sustainable technology company
- **Documents uploaded:** Sustainability charter, R&D budget ($2M/year), team of 40 engineers, brand guide (eco-first), 3-year growth strategy targeting clean energy sector
- **Idea submitted:** "Launch a smart energy monitoring SaaS for commercial buildings"
- **Expected outcome:** Aligns with values, budget fits, market demand is strong → **Proceed**

### Scenario B — Heritage Financial Group (FAILS ❌)

- **Company type:** Conservative regional bank, heavily regulated
- **Documents uploaded:** Risk policy (no speculative assets), compliance guidelines, IT budget ($200K), 5-person dev team, brand guide (trust and stability)
- **Idea submitted:** "Enter the cryptocurrency trading market and offer crypto wallets to customers"
- **Expected outcome:** Violates risk policy, under-resourced, regulatory red flags, no market expertise → **Abandon**

---

## Segment Index

| #    | Segment                             | Focus Area                                                                      |
| ---- | ----------------------------------- | ------------------------------------------------------------------------------- |
| 1    | Design System                       | Colors, typography, components                                                  |
| 2    | Frontend Foundation                 | Next.js setup, routing, config                                                  |
| 3    | Landing Page                        | Public marketing site                                                           |
| 4    | Auth Pages                          | Login, signup, onboarding                                                       |
| 5    | Dashboard                           | Home screen with stats and recent activity                                      |
| 6    | Knowledge Base UI                   | Document upload and management                                                  |
| 7    | Evaluation Submission UI            | Idea submission form                                                            |
| 8    | Live Evaluation Progress UI         | Real-time agent pipeline view                                                   |
| 9    | API Keys Setup Guide                | Keys, .env files, where each key is used                                        |
| 10   | CrewAI Planning Document            | Architecture overview, study topics                                             |
| 11   | Report Viewer UI                    | Full interactive report display                                                 |
| 12   | Settings & Admin UI                 | Team, LLM config, tenant settings                                               |
| 13   | Backend Foundation                  | FastAPI, DB, Redis, Docker                                                      |
| 14   | Auth & Multi-Tenancy                | Supabase, JWT, RBAC                                                             |
| 15   | User Data Persistence & Profile API | Store user/tenant in PostgreSQL, wire frontend                                  |
| 15.5 | API Discovery & Hook Foundation     | Create frontend hooks for every live backend API                                |
| 15.7 | Dashboard Activation                | Replace all mock data with real API calls; functional dashboard                 |
| 16   | Knowledge Base Pipeline             | Upload, extract, chunk, embed, store; wire KB endpoints to frontend immediately |
| 17   | CrewAI Agent Framework              | Base agents, multi-LLM setup, RAG tool                                          |
| 18   | Department Agents                   | 6 specialized CrewAI agents                                                     |
| 19   | Market Research Agent               | Tavily + external data synthesis                                                |
| 20   | Multi-Agent Discussion              | CrewAI crew coordination, rounds                                                |
| 21   | Conflict Detection                  | Identify tensions, resolution scenarios                                         |
| 22   | Report Synthesis & PDF              | Aggregate outputs, scoring, PDF export                                          |
| 23   | Evaluation Pipeline                 | API, Celery tasks, status flow                                                  |
| 24   | Real-Time Streaming                 | SSE events for live UI updates                                                  |
| 25   | Sample Documents & Testing          | Company docs, E2E tests, deployment                                             |

---

## Segment 1 — Design System

**Goal:** Establish the visual language before building any UI. Every component, color, and spacing decision is made here so all later segments stay consistent.

### Tasks:

- Define color palette: primary brand color (deep indigo or slate), accent (emerald for pass, rose for fail, amber for warning), neutral grays, background and surface colors
- Define typography scale: heading sizes (H1–H4), body text, monospace for scores/numbers, font family (Inter or Geist)
- Define spacing scale and border radius conventions
- Design icon set selection (Lucide React)
- Create component inventory list: Button variants (primary, secondary, ghost, destructive), Badge (status colors), Card, Modal/Dialog, Table, Tabs, Progress bar, Radar chart, Score ring, Stepper, Uploader, Sidebar nav
- Define status color system: `queued` (gray), `running` (blue pulse), `complete` (green), `failed` (red), `conditional` (amber)
- Write a `design-tokens.md` file documenting all tokens so every segment references it
- Configure Tailwind `tailwind.config.ts` with custom colors, fonts, and spacing from the design tokens

---

## Segment 2 — Frontend Foundation

**Goal:** Initialize the Next.js 14 application with all tooling configured and a working routing skeleton.

### Tasks:

- Initialize Next.js 14 project with App Router, TypeScript, and Tailwind CSS in `frontend/`
- Install and configure shadcn/ui component library
- Install supporting libraries: `recharts` (charts), `react-dropzone` (file upload), `react-query` (server state), `zustand` (UI state), `react-hook-form` + `zod` (form validation), `lucide-react` (icons), `eventsource-parser` (SSE parsing)
- Create the App Router folder structure:
  ```
  app/
  ├── (public)/         ← landing page, no auth required
  ├── (auth)/           ← login, signup
  └── (app)/            ← all authenticated pages
      ├── dashboard/
      ├── knowledge-base/
      ├── evaluations/
      │   ├── new/
      │   └── [id]/
      └── settings/
  ```
- Create `lib/api.ts` — typed fetch wrapper that attaches JWT and handles errors
- Create `lib/auth.ts` — Supabase client and session helpers
- Create `components/ui/` — base shadcn components
- Create `components/layout/` — `Sidebar`, `TopBar`, `PageWrapper`
- Configure environment variables: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Set up route middleware (`middleware.ts`) to redirect unauthenticated users from `(app)` routes to `/login`

---

## Segment 3 — Landing Page

**Goal:** Build the public-facing marketing page that explains ARIA and drives signups.

### Tasks:

- Build `app/(public)/page.tsx` — full landing page
- **Hero section:** ARIA headline, one-sentence value prop, "Get Started" and "See Demo" CTAs, animated gradient or abstract background
- **How It Works section:** 3-step visual flow — (1) Upload Knowledge Base → (2) Submit an Idea → (3) Get a Full Report. Use illustrated step cards.
- **Features section:** Cards for each major capability — Multi-Agent Analysis, Knowledge Base RAG, Live Conflict Detection, Comprehensive Reports, Multi-LLM Engine
- **Agent showcase section:** Grid of agent avatars (Marketing, Sales, Development, Design, HR, Finance, Market Research) with short role descriptions
- **Sample report preview section:** Blurred/demo screenshot of the final report with feasibility radar chart visible
- **CTA section:** "Start evaluating ideas in minutes" with signup button
- **Footer:** Links, company name, privacy policy placeholder
- Make the page fully responsive (mobile, tablet, desktop)

---

## Segment 4 — Auth Pages

**Goal:** Build login, signup, and post-login onboarding flows.

### Tasks:

- Build `app/(auth)/login/page.tsx` — email + password login form using Supabase Auth, "Forgot password" link, link to signup
- Build `app/(auth)/signup/page.tsx` — name, company name, email, password fields; creates Supabase user + tenant record on submit
- Build `app/(auth)/onboarding/page.tsx` — shown once after first signup:
  - Step 1: Confirm company name and industry
  - Step 2: Upload first document to Knowledge Base (optional, skippable)
  - Step 3: "Submit your first idea" prompt with navigation to evaluation form
- Handle Supabase auth state: persist session in cookie, redirect after login to `/dashboard`
- Show clear error messages for invalid credentials, duplicate email, weak password
- Add loading states to all form submissions

---

## Segment 5 — Dashboard

**Goal:** Build the main home screen shown after login — gives users a quick overview and entry points to all actions.

### Tasks:

- Build `app/(app)/dashboard/page.tsx`
- **Stats row (top):** 4 stat cards — Total Evaluations, Passed Ideas, Failed Ideas, Documents in Knowledge Base. Each card shows number + trend arrow.
- **Recent Evaluations table:** Last 5 evaluations with columns: Idea Title, Status badge, Overall Score, Date, View button. Click row navigates to evaluation detail.
- **Quick Actions panel:** Two large CTA buttons — "Submit New Idea" and "Upload Document"
- **Knowledge Base health widget:** Shows document count, total chunks indexed, last upload date. Warning banner if KB is empty.
- **Agent activity feed:** Last 10 agent completions across all evaluations (e.g., "Marketing Agent scored 72 on [idea]") — live-updating via polling or SSE
- Fetch all data via React Query with 30-second auto-refresh
- Add skeleton loading states for all sections

---

## Segment 6 — Knowledge Base UI

**Goal:** Build the full document management interface where companies upload their internal files.

### Tasks:

- Build `app/(app)/knowledge-base/page.tsx`
- **Upload area (top):** Drag-and-drop zone using `react-dropzone`. Accepts PDF, DOCX, TXT. Max 50MB. Shows file name + size before upload. Upload button triggers POST to backend.
- **Processing status banner:** While a document is processing, show animated progress bar with status text: "Extracting text → Chunking → Generating embeddings → Indexing"
- **Documents table:** Columns — File Name, Type (badge), Uploaded By, Date, Status (badge: `pending` / `processing` / `ready` / `error`), Actions (delete)
- **Document detail drawer:** Click a document row → side drawer shows: file metadata, chunk count, sample chunks (first 3), department tag if set
- **Department filter tags:** Allow user to tag a document to a specific department (e.g., "Finance" for budget docs). This narrows which agents retrieve it.
- **Empty state:** Illustrated empty state with text "Your Knowledge Base is empty — upload your company documents to get started"
- **Delete confirmation dialog:** "Deleting this document will remove all indexed chunks. This cannot be undone."
- Poll document status every 3 seconds while any document is `processing`

---

## Segment 7 — Evaluation Submission UI

**Goal:** Build the idea submission form — the entry point for all ARIA evaluations.

### Tasks:

- Build `app/(app)/evaluations/new/page.tsx`
- **Idea Title field:** Short text input, max 120 characters, character counter
- **Idea Description textarea:** Rich multi-line input, min 100 characters, max 2000 characters, character counter. Placeholder: "Describe the idea, the opportunity it addresses, who it targets, and why now."
- **Optional context fields (collapsible):**
  - Budget range selector (< $10K / $10K–$100K / $100K–$1M / $1M+)
  - Timeline dropdown (1–3 months / 3–6 months / 6–12 months / 12+ months)
  - Departments to involve (multi-checkbox: Marketing, Sales, Development, Design, HR, Finance)
- **LLM selector (advanced, collapsible):** Let user override which LLM runs which agent. Dropdown per agent role. Default assignments pre-filled.
- **Knowledge Base status check:** If KB is empty, show a warning: "No documents uploaded — agents will rely on general knowledge only"
- **Submit button:** "Evaluate This Idea" — on click, POST to `/evaluations`, then redirect to `/evaluations/{id}` (the live progress page)
- **Form validation:** All errors shown inline with `zod` schema validation via `react-hook-form`

---

## Segment 8 — Live Evaluation Progress UI

**Goal:** Build the real-time evaluation progress screen — the most dynamic and engaging part of the UI.

### Tasks:

- Build `app/(app)/evaluations/[id]/page.tsx` — shows both live progress and the final report (conditionally)
- **Pipeline stepper (left panel):** Vertical step list showing every stage:
  1. Policy Check (Orchestrator)
  2. Department Analysis (fan-out: 6 agents + Market Research in parallel)
  3. Agent Discussion (rounds 1–3)
  4. Conflict Detection
  5. Report Synthesis
     Each step shows: status icon (pending/spinning/check/cross), time elapsed, agent name
- **Live agent cards (center panel):** Grid of 7 agent cards. Each card shows: Agent name + LLM badge (Claude/GPT/Gemini), animated pulse while running, score ring when complete (0–100), 2-line summary when complete
- **Conflict counter (right panel):** Live counter "X conflicts detected so far" — increments as conflicts are found during discussion
- **Policy verdict banner:** After orchestrator completes, show full-width banner — green "Approved to proceed" or red "Idea rejected: [reason]"
- **SSE connection:** On page load, open `EventSource` to `/stream/evaluations/{id}`. Handle events: `agent_complete`, `conflict_detected`, `stage_update`, `complete`, `error`
- **Fallback polling:** If SSE fails, fall back to polling `/evaluations/{id}` every 5 seconds
- **Transition to report:** When `complete` event fires, smoothly scroll down to report section (no page navigation)
- **Error state:** If evaluation fails, show error message with retry option

---

## Segment 9 — API Keys Setup Guide

**Goal:** Give the developer clear, file-by-file instructions for obtaining and placing every API key before any backend code runs. No code is written in this segment — it is a developer reference.

### Frontend keys (add to `frontend/.env.local`)

| Variable                        | Where to get it                                               |
| ------------------------------- | ------------------------------------------------------------- |
| `NEXT_PUBLIC_SUPABASE_URL`      | Supabase dashboard → Project Settings → API → Project URL     |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase dashboard → Project Settings → API → anon public key |
| `NEXT_PUBLIC_API_URL`           | Set to `http://localhost:8000` for local development          |

### Backend keys (add to `backend/.env` — file scaffolded in Segment 13)

| Variable              | Where to get it                                        | Used by                                                                                                             |
| --------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| `ANTHROPIC_API_KEY`   | console.anthropic.com → API Keys → Create Key          | Orchestrator (Opus 4.6), Development Agent (Sonnet 4.6), Market Research Agent (Sonnet 4.6), Synthesizer (Opus 4.6) |
| `OPENAI_API_KEY`      | platform.openai.com → API keys → Create new secret key | Marketing Agent, Sales Agent, Finance Agent (all GPT-4o); also embedding pipeline (`text-embedding-3-small`)        |
| `GOOGLE_API_KEY`      | aistudio.google.com → Get API key                      | Design Agent, HR Agent (both Gemini 1.5 Pro)                                                                        |
| `TAVILY_API_KEY`      | app.tavily.com → API → Copy key                        | Market Research Agent (live web search)                                                                             |
| `SUPABASE_JWT_SECRET` | Supabase → Project Settings → API → JWT Secret         | Auth middleware JWT validation                                                                                      |
| `DATABASE_URL`        | Auto-set by docker-compose                             | SQLAlchemy async engine                                                                                             |
| `REDIS_URL`           | Auto-set by docker-compose                             | Celery broker + SSE pub/sub                                                                                         |

`DATABASE_URL` format: `postgresql+asyncpg://aria:aria@localhost:5432/aria`
`REDIS_URL` format: `redis://localhost:6379/0`

### Security rules (always enforce)

- `frontend/.env.local` and `backend/.env` are in `.gitignore` — **never commit them**
- Use `frontend/.env.example` and `backend/.env.example` (created in Segment 25) as your starting-point templates
- If a key is accidentally pushed to git, rotate it immediately from the provider dashboard

### Where keys are wired in code

- **Frontend** — Next.js reads `NEXT_PUBLIC_*` variables automatically at build time via `process.env`
- **Backend** — `backend/app/config.py` (Segment 13) uses Pydantic `BaseSettings` to load all backend env vars
- **LLM clients** — instantiated in `backend/app/agents/llm_config.py` (Segment 17) using the keys above

---

## Segment 10 — CrewAI Planning Document

**Goal:** Create `CrewAI-Planning.md` at the project root so the developer understands the framework before any agent code is written (Segments 17–20). No code is written in this segment.

### Tasks

- Create `CrewAI-Planning.md` at the project root with the content described below.

### What goes in `CrewAI-Planning.md`

**One-liner:**
CrewAI is a Python framework for orchestrating multiple autonomous AI agents that each have a role, goal, backstory, and toolset — they collaborate on tasks and pass results to each other in a defined sequential or parallel process.

**ARIA agent architecture:**

```
Orchestrator (policy check) — Claude Opus 4.6
        ↓ if approved
┌─────────────────────────────────────────┐
│  Parallel fan-out (asyncio.gather)      │
│  Marketing (GPT-4o)                     │
│  Sales (GPT-4o)                         │
│  Development (Claude Sonnet 4.6)        │
│  Design (Gemini 1.5 Pro)                │
│  HR (Gemini 1.5 Pro)                    │
│  Finance (GPT-4o)                       │
│  Market Research (Claude Sonnet + Tavily│
└─────────────────────────────────────────┘
        ↓ all 7 complete
Conflict Detector  (Claude Sonnet — analyses all outputs)
        ↓
Discussion Rounds  (up to 3 rounds of cross-agent reactions)
        ↓
Synthesizer        (Claude Opus 4.6 → final report + PDF)
```

**Key CrewAI concepts used in ARIA:**

- `Agent(role, goal, backstory, llm, tools)` — one instance per department
- `Task(description, agent, expected_output)` — one analysis task per agent run
- `Crew(agents, tasks, process=Process.sequential)` — top-level runner per evaluation
- Custom `BaseTool` subclass for RAG (`CompanyKnowledgeBase`) and web search (`TavilySearch`)
- `output_pydantic=` on each Task to enforce structured JSON output (score, analysis, concerns, recommendations, budget_estimate, verdict)
- Results flow: each Task output is stored as an `AgentRun` DB record before being passed downstream

**Topics to study (in priority order):**

1. **CrewAI Quickstart** — official docs at docs.crewai.com: Agent, Task, Crew basics
2. **Custom Tools** — writing a `@tool` decorated function or subclassing `BaseTool`
3. **Multi-LLM setup** — passing a different `llm=` instance per Agent
4. **Process types** — `Process.sequential` vs `Process.hierarchical` and when to use each
5. **asyncio + CrewAI** — running multiple Crew instances concurrently with `asyncio.gather`
6. **Pydantic output parsing** — using `output_pydantic=MyModel` on a Task for validated structured output
7. **LangChain LLM wrappers** — CrewAI uses LangChain internally; understand `ChatAnthropic`, `ChatOpenAI`, `ChatGoogleGenerativeAI`
8. **Prompt caching (Anthropic)** — the `cache_control` header on Claude API calls to reduce cost on repeated system prompts

---

## Segment 11 — Report Viewer UI

**Goal:** Build the comprehensive report display shown after evaluation completes. This is the deliverable users come for.

### Tasks:

- Build `components/report/ReportViewer.tsx` — rendered inside the evaluation detail page after completion
- **Report header:** Idea title, final recommendation badge (Proceed / Modify / Pause / Abandon) with color coding, confidence score, evaluation date, "Download PDF" button
- **Tab navigation:** Five tabs — Overview · Departments · Market Research · Conflicts · Cost Breakdown
- **Tab 1 — Overview:**
  - Feasibility Radar Chart (Recharts `RadarChart`) with 6 axes: Overall, Financial, Market, Technical, Operational, Strategic
  - Executive summary paragraph (from Synthesizer agent)
  - Policy verdict card with reason text
  - Quick verdict cards per department (small colored badges)
- **Tab 2 — Departments:**
  - One accordion card per department (Marketing, Sales, Development, Design, HR, Finance)
  - Each card shows: Score ring, Verdict badge, Full analysis text, Key concerns list, Recommendations list, Budget estimate table
- **Tab 3 — Market Research:**
  - Market size estimate, demand signal list, trend direction indicator (up/flat/down arrow)
  - Competitor count + top competitors table
  - Market score ring
  - Source links from Tavily results
- **Tab 4 — Conflicts:**
  - List of all detected conflicts, each showing: Departments involved, Conflict type badge, Severity badge (low/medium/high/critical), Description
  - Expandable resolution scenarios per conflict: accordion showing 2–3 scenarios with title, description, and tradeoffs
  - Conflict summary: "X conflicts detected, Y high/critical severity"
- **Tab 5 — Cost Breakdown:**
  - Table: Cost item, Estimated range, Department, Notes
  - Total estimated range at bottom
  - Bar chart of costs by department
- **PDF download:** Button calls `GET /evaluations/{id}/report/pdf` and triggers browser download

---

## Segment 12 — Settings & Admin UI

**Goal:** Build team management, LLM configuration, and tenant settings pages.

### Tasks:

- Build `app/(app)/settings/page.tsx` with sub-sections:
- **Team Management section:**
  - User table: Name, Email, Role badge (admin / analyst / viewer), Last active, Actions (change role, remove)
  - "Invite Team Member" button → modal with email + role selector → sends invite via Supabase
- **LLM Configuration section:**
  - Table of all 9 agent roles, current LLM assigned, dropdown to change
  - API key status indicators (green checkmark if key present in env, red X if missing)
  - "Test Connection" button per LLM — calls backend to verify API key works
- **Company Profile section:**
  - Company name, industry, description fields
  - Save button → PATCH `/tenants/{id}`
- **Knowledge Base stats section:**
  - Total documents, total chunks, last indexed date, storage used estimate
  - "Clear All Documents" danger button with confirmation dialog
- **Danger Zone section:**
  - "Delete all evaluations" — with strong confirmation (type company name to confirm)

---

## Segment 13 — Backend Foundation

**Goal:** Set up the complete backend infrastructure from scratch — FastAPI app, database, Redis, Docker.

### Tasks:

- Initialize Python project with `pyproject.toml` (Poetry): FastAPI, Uvicorn, SQLAlchemy 2.0 async, Asyncpg, Alembic, Pydantic 2, CrewAI, Anthropic, OpenAI, google-generativeai, LlamaIndex, pgvector, Celery, Redis, python-multipart, WeasyPrint, httpx, structlog, slowapi
- Create `backend/app/main.py` — FastAPI app with CORS, trusted host, rate limit middleware. Register all API routers.
- Create `backend/app/config.py` — Pydantic Settings reading all env vars: DB URL, Redis URL, Supabase keys, Anthropic/OpenAI/Google API keys, Tavily key, upload limits
- Create `backend/app/database.py` — async SQLAlchemy engine, session factory, `get_db` dependency
- Define all SQLAlchemy models in `backend/app/models/`:
  - `Tenant` — id, name, industry, settings JSONB, created_at
  - `User` — id, tenant_id, email, role (admin/analyst/viewer), supabase_uid
  - `KBDocument` — id, tenant_id, filename, file_path, status, chunk_count, created_at
  - `KBChunk` — id, document_id, tenant_id, content, embedding (pgvector 1536-dim), metadata JSONB
  - `Evaluation` — id, tenant_id, title, description, status, policy_verdict, created_at, completed_at
  - `AgentRun` — id, evaluation_id, agent_type, llm_used, raw_output, structured_result JSONB, tokens_used, duration_seconds
  - `DiscussionRound` — id, evaluation_id, round_number, agent_type, content
  - `Conflict` — id, evaluation_id, agent_a, agent_b, conflict_type, severity, description, resolution_scenarios JSONB
  - `Report` — id, evaluation_id, feasibility_scores JSONB, cost_breakdown JSONB, market_analysis JSONB, recommendation, confidence_score, pdf_path, full_report JSONB
- Run `alembic revision --autogenerate -m "initial_schema"` and `alembic upgrade head`
- Write `docker-compose.yml`:
  - `postgres` (postgres:16 + pgvector extension)
  - `redis` (redis:7-alpine)
  - `backend` (FastAPI on port 8000)
  - `celery_worker` (same image, `celery -A app.tasks.celery_app worker`)
- Write `backend/scripts/seed.py` — creates two tenants (GreenTech + Heritage Financial), admin users, and sample documents for each

---

## Segment 14 — Auth & Multi-Tenancy

**Goal:** Implement JWT-based auth with Supabase and per-tenant data isolation.

### Tasks:

- Create `backend/app/middleware/auth.py` — decode Supabase JWT from `Authorization: Bearer` header, look up `User` record by `supabase_uid`, attach `current_user` and `current_tenant` to request state
- Create `backend/app/dependencies.py` — FastAPI `Depends()` functions:
  - `get_current_user` — requires valid JWT
  - `require_admin` — user role must be `admin`
  - `require_analyst` — user role must be `admin` or `analyst`
- Implement `POST /auth/login` — validates Supabase credentials, returns JWT + user info
- Implement `GET /auth/me` — returns current user + tenant details
- Implement `POST /auth/signup` — creates Supabase user + `Tenant` record + `User` record in one transaction
- Implement all user management routes: list users, invite (create user record), change role, remove user
- Implement tenant settings routes: GET tenant, PATCH tenant settings
- All queries filter by `tenant_id` — no cross-tenant data leakage

---

## Segment 15 — User Data Persistence & Profile API

**Goal:** Persist every user's identity and company profile to PostgreSQL immediately after signup and onboarding. Replace all `sessionStorage` usage with real database records. Wire the frontend to call the live API so data is never lost on page refresh.

### Backend Tasks:

- Create `backend/app/routers/auth.py`:
  - `POST /auth/signup` — receives `{ email, full_name, company_name, supabase_uid }`, creates `Tenant` row + `User` row (role=`admin`) in a single DB transaction. Returns `{ user, tenant }`.
  - `POST /auth/login` — validates Supabase JWT, returns JWT + `{ user, tenant }` from DB
  - `GET /auth/me` — decodes JWT, looks up `User` by `supabase_uid`, returns `{ user, tenant }`
- Create `backend/app/routers/tenants.py`:
  - `GET /tenants/{id}` — return tenant profile
  - `PATCH /tenants/{id}` — update `name`, `industry`, `description`, `settings` fields (used by onboarding Step 1 and Settings page)
- Create `backend/app/routers/users.py`:
  - `GET /users` — list all users in current tenant (admin only)
  - `PATCH /users/{id}/role` — change user role (admin only)
  - `DELETE /users/{id}` — remove user from tenant (admin only)
- Create `backend/app/schemas/user.py` — Pydantic models: `UserCreate`, `UserRead`, `UserRoleUpdate`
- Create `backend/app/schemas/tenant.py` — Pydantic models: `TenantCreate`, `TenantRead`, `TenantUpdate`
- Create `backend/app/services/user_service.py`:
  - `create_user(db, data)` — insert `User` row, return ORM object
  - `get_user_by_supabase_uid(db, uid)` — lookup for auth middleware
  - `list_users(db, tenant_id)` — all users in a tenant
  - `update_role(db, user_id, role)` — change role
  - `delete_user(db, user_id)` — remove user
- Create `backend/app/services/tenant_service.py`:
  - `create_tenant(db, data)` — insert `Tenant` row
  - `get_tenant(db, id)` — fetch by id
  - `update_tenant(db, id, data)` — partial update (name, industry, description, settings)
- Register routers in `backend/app/main.py`: include `auth`, `tenants`, `users`
- All endpoints protected by `get_current_user` dependency except `POST /auth/signup` and `POST /auth/login`
- All tenant/user queries filter by `tenant_id` from the JWT — no cross-tenant leakage

### Frontend Tasks:

- Update `frontend/app/(auth)/signup/page.tsx`:
  - After Supabase `signUp()` succeeds, call `POST /auth/signup` via `api.post()` to create DB records
  - Pass `{ email, full_name, company_name, supabase_uid }` from auth response
  - Remove `sessionStorage.setItem("aria_onboarding_company")` — company name now lives in DB
- Update `frontend/app/(auth)/onboarding/page.tsx` Step 1:
  - Call `PATCH /tenants/{id}` with `{ name: companyName, industry }` instead of writing to `sessionStorage`
  - Read tenant id from `useCurrentUser` hook
  - Remove `sessionStorage.removeItem` cleanup calls
- Create `frontend/lib/hooks/useCurrentUser.ts`:
  - React Query hook: `useQuery({ queryKey: ['me'], queryFn: () => api.get('/auth/me') })`
  - Returns `{ user, tenant, isLoading, isError }`
  - Used by TopBar avatar, Settings page, and anywhere user/tenant data is needed
- Update `frontend/components/layout/TopBar.tsx`:
  - Replace hardcoded `"U"` avatar with first letter of `user.full_name` from `useCurrentUser`
  - Show tenant name in the header when loaded

### Data stored after this segment:

**`tenants` table** — `id`, `name`, `industry`, `description`, `settings JSONB`, `created_at`

**`users` table** — `id`, `tenant_id`, `email`, `full_name`, `role`, `supabase_uid`, `created_at`

---

---

> **API Wiring Rule (applies to all segments from 16 onward):**
> Every backend segment that adds new FastAPI routes must immediately include the corresponding
> frontend hook(s) in `frontend/lib/hooks/` and wire them into the relevant page.
> No segment ships with mock data or `setTimeout` placeholders if a real API exists.

---

## Segment 15.5 — API Discovery & Hook Foundation

**Goal:** Search every implemented backend route, create a typed frontend hook for each one, and confirm all hooks are consumed by the correct pages. This is a pure frontend integration pass — no new backend code.

### Completed tasks:

- **`useCurrentUser`** (`GET /auth/me`) — returns `{ user, tenant }` with demo-mode fallback from `sessionStorage`. Used by TopBar, Settings, Onboarding.
- **`useUsers`** (`GET /users`) — fetches all users in the tenant. Used by Settings team table.
- **`useInviteUser`** (`POST /users/invite`) — sends invite; invalidates `["users"]` cache. Used by Settings invite dialog.
- **`useUpdateRole`** (`PATCH /users/{id}/role`) — changes role; invalidates cache. Used by Settings role dropdown.
- **`useDeleteUser`** (`DELETE /users/{id}`) — removes user; invalidates cache. Used by Settings remove dialog.
- **`useUpdateTenant`** (`PATCH /tenants/{id}`) — updates company profile; invalidates `["me"]` cache. Used by Settings company profile + Onboarding step 1.
- **Bug fixes applied:** demo-mode notice on login page, logout dropdown on TopBar avatar, demo tenant name shown from `sessionStorage`.

---

## Segment 15.7 — Dashboard Activation

**Goal:** Replace every `MOCK_*` constant and `setTimeout` stub in `dashboard/page.tsx` with real API calls once the corresponding backend endpoints exist. Until then, document exactly which backend route each widget needs.

### Dashboard widgets → backend endpoints needed:

| Widget                                     | Data needed         | Backend endpoint (built in segment)       |
| ------------------------------------------ | ------------------- | ----------------------------------------- |
| Stats: Total / Passed / Failed evaluations | Count by outcome    | `GET /evaluations/stats` (Segment 23)     |
| Stats: KB Documents                        | Document count      | `GET /knowledge-base/health` (Segment 16) |
| Recent Evaluations table                   | List of evaluations | `GET /evaluations` (Segment 23)           |
| Knowledge Base health card                 | Doc + chunk count   | `GET /knowledge-base/health` (Segment 16) |
| Agent Activity feed                        | Agent run events    | `GET /activity` (Segment 23)              |

### Tasks (execute as each backend segment completes):

- **After Segment 16:** Replace `useKBHealth` mock → `api.get("/knowledge-base/health")`. Update KB stats in Settings too.
- **After Segment 23:** Replace `useDashboardStats`, `useRecentEvaluations`, `useAgentActivity` mocks → real endpoints. Dashboard becomes fully functional.

### Frontend hooks to create (in order, as backend is built):

- `frontend/lib/hooks/useKBHealth.ts` — after Segment 16
- `frontend/lib/hooks/useEvaluations.ts` — after Segment 23
- `frontend/lib/hooks/useDashboardStats.ts` — after Segment 23
- `frontend/lib/hooks/useActivity.ts` — after Segment 23

---

## Segment 16 — Knowledge Base Pipeline

**Goal:** Build document upload, text extraction, chunking, embedding, and vector storage pipeline.

### Tasks:

- Implement `POST /knowledge-base/upload` — accept multipart file upload, validate type (PDF/DOCX/TXT) and size (50MB max), save to `uploads/{tenant_id}/` directory, create `KBDocument` record with status `pending`, enqueue Celery task `process_document`
- Implement `GET /knowledge-base` — paginated list of documents for current tenant, filtered by status if provided
- Implement `DELETE /knowledge-base/{id}` — delete file from disk, delete all `KBChunk` records, delete `KBDocument` record
- Implement Celery task `process_document(document_id)`:
  1. Extract text: use `PyMuPDF` for PDF, `python-docx` for DOCX, plain `open()` for TXT
  2. Clean and normalize text (strip extra whitespace, remove headers/footers)
  3. Chunk: split into 512-token chunks with 50-token overlap using `tiktoken`
  4. Embed each chunk via OpenAI `text-embedding-3-small` (batch requests, max 100 chunks/batch)
  5. Bulk insert `KBChunk` records with pgvector embeddings
  6. Update `KBDocument` status to `ready` (or `error` with message on failure)
- Create `backend/app/services/kb_service.py`:
  - `retrieve(tenant_id, query, top_k=5, department=None)` — embed query, cosine-similarity search via pgvector `<=>` operator, return top-k chunks as formatted context string
  - Used by all CrewAI agents as their RAG tool
- **Frontend wiring (API Wiring Rule):** immediately after backend routes are ready:
  - Create `frontend/lib/hooks/useKBHealth.ts` — `GET /knowledge-base/health`
  - Create `frontend/lib/hooks/useKBDocuments.ts` — `GET /knowledge-base`, `POST /knowledge-base/upload`, `DELETE /knowledge-base/{id}`
  - Wire `useKBHealth` into `dashboard/page.tsx` KB health card (replace mock)
  - Wire `useKBHealth` into `settings/page.tsx` KB stats section (replace `—` placeholders)
  - Wire `useKBDocuments` into `knowledge-base/page.tsx` document list + upload + delete

---

## Segment 17 — CrewAI Agent Framework

**Goal:** Set up the CrewAI foundation — multi-LLM configuration, the shared RAG tool, and the base agent pattern.

### Tasks:

- Install and configure CrewAI: `crewai`, `crewai-tools`
- Create `backend/app/agents/llm_config.py` — initialize LLM instances:
  - `claude_opus` = Anthropic Claude Opus 4.6
  - `claude_sonnet` = Anthropic Claude Sonnet 4.6
  - `gpt4o` = OpenAI GPT-4o
  - `gemini_pro` = Google Gemini 1.5 Pro
  - All instances configured from `settings` env vars
  - Enable prompt caching on Claude instances (`cache_control` header)
- Create `backend/app/agents/tools/rag_tool.py` — custom CrewAI `Tool`:
  - Name: `CompanyKnowledgeBase`
  - Input: query string
  - Action: calls `kb_service.retrieve(tenant_id, query)` and returns formatted context
  - Used by all department agents to ground analysis in company-specific documents
- Create `backend/app/agents/tools/tavily_tool.py` — custom CrewAI `Tool` wrapping Tavily search API
- Create `backend/app/agents/base_crew.py`:
  - `build_agent(role, goal, backstory, llm, tools)` → returns `crewai.Agent`
  - `build_task(description, agent, expected_output)` → returns `crewai.Task`
  - `run_crew(agents, tasks, process) → dict` — runs crew, captures output, returns structured results
- Define the standard structured output format all agents must return (JSON schema for `feasibility_score`, `analysis`, `key_concerns`, `recommendations`, `budget_estimate`, `verdict`)
- All agent outputs are validated with Pydantic before being persisted

---

## Segment 18 — Department Agents

**Goal:** Implement the 6 department CrewAI agents — each with a domain-specific role, backstory, system prompt, and assigned LLM.

### Tasks:

- Create `backend/app/agents/orchestrator.py`:
  - LLM: Claude Opus 4.6
  - Role: "Chief Policy Officer"
  - Goal: Check if the idea aligns with company policy, values, and strategic direction
  - Backstory: Trained on company policies, compliance requirements, and strategic goals
  - Tool: `CompanyKnowledgeBase` (filtered to policy documents)
  - Returns: `{verdict: approved|rejected|conditional, reason, conditions, policy_references}`
  - If `rejected` → all downstream agents are skipped

- Create `backend/app/agents/department/marketing.py`:
  - LLM: GPT-4o
  - Role: "Chief Marketing Officer"
  - Analyzes: brand alignment, target audience, go-to-market strategy, marketing budget requirements, campaign feasibility
  - Returns: feasibility score, key concerns, recommendations, budget estimate

- Create `backend/app/agents/department/sales.py`:
  - LLM: GPT-4o
  - Role: "VP of Sales"
  - Analyzes: revenue potential, sales cycle, customer acquisition cost, pipeline fit, pricing strategy
  - Returns: feasibility score, projected ARR range, sales team requirements

- Create `backend/app/agents/department/development.py`:
  - LLM: Claude Sonnet 4.6
  - Role: "Chief Technology Officer"
  - Analyzes: technical feasibility, development effort, technology stack requirements, infrastructure cost, timeline realism
  - Returns: feasibility score, estimated sprint count, team size required, tech debt risks

- Create `backend/app/agents/department/design.py`:
  - LLM: Gemini 1.5 Pro
  - Role: "Head of Product Design"
  - Analyzes: user experience implications, design complexity, brand consistency, accessibility considerations, prototype effort
  - Returns: feasibility score, UX concerns, design resource estimate

- Create `backend/app/agents/department/hr.py`:
  - LLM: Gemini 1.5 Pro
  - Role: "Chief People Officer"
  - Analyzes: hiring requirements, existing skill gaps, team capacity, culture fit, onboarding timeline
  - Returns: feasibility score, headcount required, skill gap analysis, culture risks

- Create `backend/app/agents/department/finance.py`:
  - LLM: GPT-4o
  - Role: "Chief Financial Officer"
  - Analyzes: total cost of ownership, ROI timeline, budget availability (from KB docs), financial risk, break-even analysis
  - Returns: feasibility score, cost estimate (low/high range), payback period, risk rating

---

## Segment 19 — Market Research Agent

**Goal:** Implement the external-facing Market Research agent that uses Tavily to scan live data.

### Tasks:

- Create `backend/app/agents/market_research.py`:
  - LLM: Claude Sonnet 4.6
  - Role: "Market Intelligence Analyst"
  - Goal: Determine whether the external world wants what the company is considering building
  - Tools: `TavilySearchTool` (runs 4 targeted searches), `CompanyKnowledgeBase` (for company's prior market research)
  - **Search queries generated per evaluation:**
    1. `"{idea_topic} market size 2024 2025"`
    2. `"{idea_topic} competitors landscape"`
    3. `"{idea_topic} customer demand trends"`
    4. `"{idea_topic} industry news recent"`
  - Synthesizes search results into structured market analysis
  - Returns: `{market_size_estimate, demand_signals[], competitor_count, top_competitors[], trend_direction, market_score, source_urls[]}`
- Market Research agent runs **in parallel** with the 6 department agents (not sequentially)

---

## Segment 20 — Multi-Agent Discussion

**Goal:** Implement the structured discussion phase where agents react to each other's findings.

### Tasks:

- Create `backend/app/agents/discussion.py`
- After all 7 agents (6 departments + market research) complete their initial analysis, collect all structured outputs
- **Round 1 — Cross-department reactions:**
  - Each agent receives the outputs of the other 6 agents
  - Each agent generates a 1–2 paragraph reaction: "Given what Finance found, here is my revised concern..."
  - Run all 7 reactions in parallel using `asyncio.gather` (each is a separate CrewAI task)
  - Persist each reaction as a `DiscussionRound` record (round_number=1)
- **Round 2 — Conflict-focused responses:**
  - Feed detected conflicts (from Segment 18) back to the relevant agents
  - Each involved agent proposes a resolution from their department's perspective
  - Persist as `DiscussionRound` records (round_number=2)
- **Round 3 — Final position statement (optional, only if high/critical conflicts exist):**
  - Each affected agent states their final position after seeing resolution proposals
  - Persist as `DiscussionRound` records (round_number=3)
- Maximum 3 rounds total. If no high/critical conflicts, stop after Round 1.
- Return all discussion rounds as ordered list for report synthesis

---

## Segment 21 — Conflict Detection & Resolution

**Goal:** Identify every tension point between agent findings, categorize them, and generate resolution scenarios.

### Tasks:

- Create `backend/app/agents/conflict_detector.py`
- Input: all 7 agent structured outputs + discussion round outputs
- Use Claude Sonnet to analyze all outputs and identify conflicts
- **Conflict types to detect:**
  - `budget_mismatch` — Finance's cost estimate conflicts with another department's budget assumption
  - `timeline_clash` — Development's timeline conflicts with Sales' urgency or Marketing's launch plan
  - `resource_overlap` — Two departments claim the same team capacity
  - `strategic_misalignment` — One department's direction conflicts with company strategy (from KB)
  - `market_reality_gap` — Market Research findings contradict a department's demand assumption
  - `risk_tolerance_conflict` — Finance/HR risk assessment contradicts another department's optimism
- For each conflict:
  - Identify the two (or more) agents involved
  - Assign `severity`: `low` / `medium` / `high` / `critical`
  - Write a clear description of the specific tension
  - Generate **2–3 resolution scenarios**, each with: title, description, tradeoffs (what each side gives up)
- Persist all conflicts to `Conflict` table
- Return conflict list for report and for Round 2 of discussion

---

## Segment 22 — Report Synthesis & PDF Generation

**Goal:** Aggregate all agent outputs, discussions, and conflicts into a single comprehensive report. Generate PDF.

### Tasks:

- Create `backend/app/agents/synthesizer.py`:
  - LLM: Claude Opus 4.6
  - Input: all agent outputs, market research, discussion rounds, conflict list
  - Write 3–4 paragraph executive summary
  - Write final recommendation with justification (proceed / modify / pause / abandon)
  - Calculate confidence score (0–100) based on conflict severity distribution and score variance
- Create `backend/app/services/report_service.py`:
  - `calculate_feasibility_scores(agent_outputs)` → weighted averages for 6 dimensions
  - `build_cost_breakdown(agent_outputs)` → consolidated cost table from all dept estimates
  - `assemble_report(evaluation_id)` → collects everything into `ReportData` dict
  - `generate_pdf(report_data)` → render Jinja2 HTML template → WeasyPrint → PDF bytes → save to `reports/{id}.pdf`
- Create `backend/templates/report.html` — styled HTML report template with:
  - Company logo placeholder, ARIA branding
  - All report sections in print-friendly layout
  - Inline CSS (WeasyPrint cannot load external CSS)
- Persist `Report` record with all JSON data + PDF path
- Update `Evaluation` status to `complete`

---

## Segment 23 — Evaluation Pipeline

**Goal:** Wire the entire evaluation workflow together via API endpoints and Celery background tasks.

### Tasks:

- Implement `POST /evaluations`:
  - Validate request body (title, description, optional overrides)
  - Create `Evaluation` record with status `queued`
  - Enqueue Celery task `run_evaluation(evaluation_id)`
  - Return `{id, status: "queued"}`
- Implement `GET /evaluations` — paginated list with status, scores, dates (tenant-scoped)
- Implement `GET /evaluations/{id}` — full evaluation with all agent runs, discussions, conflicts, and report (if complete)
- Implement `GET /evaluations/{id}/report/pdf` — stream PDF file as download response
- Implement Celery task `run_evaluation(evaluation_id)`:
  ```
  1. Update status → "policy_check"
  2. Run Orchestrator agent
  3. If rejected → update status "failed", publish SSE event, stop
  4. Update status → "running"
  5. Run 7 agents in parallel (asyncio.gather):
     - Marketing, Sales, Development, Design, HR, Finance, MarketResearch
  6. Persist all 7 AgentRun records
  7. Update status → "conflict_detection"
  8. Run conflict detector
  9. Persist Conflict records
  10. Update status → "discussion"
  11. Run discussion rounds (1–3)
  12. Persist DiscussionRound records
  13. Update status → "synthesis"
  14. Run synthesizer
  15. Generate PDF
  16. Persist Report record
  17. Update status → "complete"
  18. Publish "complete" SSE event
  ```
- Publish Redis pub/sub event after every status change (for SSE)

---

## Segment 24 — Real-Time Streaming

**Goal:** Implement SSE endpoint so the frontend receives live updates as the evaluation runs.

### Tasks:

- Implement `GET /stream/evaluations/{id}` — SSE endpoint using FastAPI `StreamingResponse`
- On connect: subscribe to Redis pub/sub channel `eval:{id}`
- Stream events as they are published by the Celery task:
  - `event: status_update` — `{stage: "policy_check"}` when status changes
  - `event: agent_complete` — `{agent: "marketing", score: 72, verdict: "proceed"}` when an agent finishes
  - `event: conflict_detected` — `{count: 3, latest: {type: "budget_mismatch", severity: "high"}}` when conflicts found
  - `event: discussion_round` — `{round: 1, agent: "finance"}` as reactions complete
  - `event: complete` — `{report_id: "..."}` when evaluation fully done
  - `event: error` — `{message: "..."}` if task fails
- Handle client disconnect gracefully (unsubscribe from Redis)
- Include heartbeat event every 15 seconds to keep connection alive

---

## Segment 25 — Sample Documents & Testing

**Goal:** Create realistic company documents for both test scenarios, run end-to-end tests, and set up deployment.

### Tasks:

**GreenTech Innovations documents (PASS scenario):**

- `greentech_sustainability_charter.pdf` — company values, eco-first principles, no fossil fuel partnerships
- `greentech_rd_budget_2025.pdf` — R&D budget $2M, allocations per team, approval thresholds
- `greentech_team_structure.docx` — 40 engineers, 8 product managers, 5 designers, marketing team
- `greentech_growth_strategy.docx` — 3-year plan targeting clean energy, smart infrastructure, IoT
- `greentech_brand_guide.pdf` — tone of voice, visual identity, positioning (premium, sustainable)

**Heritage Financial Group documents (FAIL scenario):**

- `heritage_risk_policy.pdf` — conservative risk framework, no speculative assets, no unregulated markets
- `heritage_compliance_guide.pdf` — regulatory requirements, KYC/AML obligations, prohibited activities
- `heritage_it_budget_2025.docx` — IT budget $200K, 5-person dev team, no cloud-native infrastructure
- `heritage_brand_guide.pdf` — trust, stability, traditional banking values
- `heritage_team_org.docx` — 200 staff, mostly traditional banking roles, no blockchain/crypto expertise

**End-to-end test (`tests/e2e/test_full_evaluation.py`):**

- Test 1: Upload GreenTech docs → submit smart energy SaaS idea → verify status reaches `complete` → verify recommendation is `proceed` or `modify`
- Test 2: Upload Heritage docs → submit crypto trading idea → verify orchestrator returns `rejected` → verify evaluation stops after policy check
- Test 3: Verify SSE events are emitted in correct order for a running evaluation
- Test 4: Verify PDF report is generated and downloadable

**Unit tests (`tests/unit/`):**

- Test each agent with mocked LLM response and mocked RAG output
- Test conflict detector with synthetic agent outputs containing known conflicts
- Test scoring calculator with edge cases (all zeros, all 100s, mixed)
- Test document chunking with short, long, and empty documents

**Deployment:**

- Finalize `docker-compose.yml` for local dev (all services in one command)
- Write `Dockerfile` for backend with multi-stage build
- Write `Dockerfile` for frontend with Next.js production build
- Write `.env.example` with every required environment variable documented
- Write `README.md` with setup instructions: clone → fill `.env` → `docker-compose up` → open `localhost:3000`

---

## Full Build Order

```
Segment 1  → Design System (tokens, component list)
Segment 2  → Frontend Foundation (Next.js, routing, tooling)
Segment 3  → Landing Page
Segment 4  → Auth Pages
Segment 5  → Dashboard
Segment 6  → Knowledge Base UI
Segment 7  → Evaluation Submission UI
Segment 8  → Live Evaluation Progress UI
Segment 9  → API Keys Setup Guide
Segment 10 → CrewAI Planning Document
Segment 11 → Report Viewer UI
Segment 12 → Settings & Admin UI
           ↓ (frontend complete — now backend)
Segment 13 → Backend Foundation (FastAPI, DB, Docker)
Segment 14 → Auth & Multi-Tenancy
Segment 15 → User Data Persistence & Profile API
Segment 16 → Knowledge Base Pipeline
Segment 17 → CrewAI Agent Framework
Segment 18 → Department Agents (6 agents)
Segment 19 → Market Research Agent
Segment 20 → Multi-Agent Discussion
Segment 21 → Conflict Detection
Segment 22 → Report Synthesis & PDF
Segment 23 → Evaluation Pipeline (API + Celery)
Segment 24 → Real-Time Streaming (SSE)
Segment 25 → Sample Documents & Testing
```
