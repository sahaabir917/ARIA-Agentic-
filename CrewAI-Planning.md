# CrewAI Planning — ARIA Project

## What is CrewAI (one line)

CrewAI is a Python framework for orchestrating multiple autonomous AI agents that each have a role, goal, backstory, and toolset — they collaborate on tasks and pass results to each other in a defined sequential or parallel process.

---

## ARIA Agent Architecture

```
Orchestrator — Claude Opus 4.6
  Role: Chief Policy Officer
  Checks idea against company values, strategy, and compliance docs
        │
        │ if approved ↓   (if rejected → evaluation stops here)
        │
┌───────────────────────────────────────────────────────┐
│              Parallel fan-out (asyncio.gather)         │
│                                                        │
│  Marketing Agent     → GPT-4o     (CMO)               │
│  Sales Agent         → GPT-4o     (VP Sales)          │
│  Development Agent   → Sonnet 4.6 (CTO)               │
│  Design Agent        → Gemini Pro (Head of Design)    │
│  HR Agent            → Gemini Pro (CPO)               │
│  Finance Agent       → GPT-4o     (CFO)               │
│  Market Research     → Sonnet 4.6 + Tavily (Analyst)  │
└───────────────────────────────────────────────────────┘
        │
        │ all 7 agents complete ↓
        │
Conflict Detector — Claude Sonnet 4.6
  Analyses all 7 outputs for tensions (budget, timeline, resources, etc.)
  Produces: list of Conflict records with severity + resolution scenarios
        │
        ↓
Discussion Rounds — up to 3 rounds
  Round 1: each agent reacts to the other 6 outputs
  Round 2: agents respond to detected conflicts (if high/critical exist)
  Round 3: final position statements (only if critical conflicts remain)
        │
        ↓
Synthesizer — Claude Opus 4.6
  Aggregates everything into a single executive report
  Outputs: recommendation (Proceed / Modify / Pause / Abandon),
           confidence score, executive summary, feasibility radar scores
  Generates PDF via WeasyPrint
```

---

## Key CrewAI Concepts Used in ARIA

| Concept | How ARIA uses it |
|---------|-----------------|
| `Agent(role, goal, backstory, llm, tools)` | One instance per department agent; backstory grounds it in the company's KB |
| `Task(description, agent, expected_output)` | One analysis task per agent run; `expected_output` is a Pydantic schema string |
| `Crew(agents, tasks, process=Process.sequential)` | Wraps each mini-pipeline (policy check, fan-out group, synthesis) |
| `output_pydantic=AgentOutput` | Forces each Task to return a validated JSON blob |
| `BaseTool` subclass | `CompanyKnowledgeBase` tool — embeds the query, does pgvector search, returns context chunks |
| `BaseTool` subclass | `TavilySearchTool` — wraps Tavily REST API for live web search |
| `asyncio.gather` | Runs all 7 parallel agents concurrently, not waiting for one before starting the next |

### Standard agent output schema (every dept agent returns this)
```python
class AgentOutput(BaseModel):
    feasibility_score: int          # 0–100
    verdict: str                    # "proceed" | "modify" | "pause" | "abandon"
    analysis: str                   # 2–4 paragraph analysis
    key_concerns: list[str]
    recommendations: list[str]
    budget_estimate: dict           # {"low": int, "high": int, "currency": "USD"}
```

---

## Topics to Study (in priority order)

### 1. CrewAI Quickstart
Read the official docs: **docs.crewai.com**
Understand: Agent, Task, Crew, Process — the four core building blocks.
Try the "Hello World" crew before writing any ARIA agent code.

### 2. Custom Tools
Learn to write a `@tool` decorated function and a `BaseTool` subclass.
ARIA needs two custom tools: one for vector search (RAG) and one for Tavily.

### 3. Multi-LLM Setup
Learn how to pass a different `llm=` instance to each Agent.
CrewAI accepts LangChain chat model objects — one per agent.

### 4. Process Types
Understand `Process.sequential` (one task at a time) vs
`Process.hierarchical` (manager delegates to workers).
ARIA uses sequential within each Crew, but kicks off multiple Crews in parallel.

### 5. asyncio + CrewAI
Learn how to wrap `crew.kickoff()` in an async function and run multiple
crews simultaneously with `asyncio.gather()`.
This is how the 7 parallel department agents run in ARIA.

### 6. Pydantic Output Parsing
Learn `Task(output_pydantic=MyModel)` — CrewAI parses the LLM's raw string
output into a validated Pydantic model automatically.
Required to enforce the structured AgentOutput schema above.

### 7. LangChain LLM Wrappers
CrewAI uses LangChain under the hood. Study:
- `ChatAnthropic` — for Claude Opus and Sonnet
- `ChatOpenAI` — for GPT-4o
- `ChatGoogleGenerativeAI` — for Gemini 1.5 Pro

Each is initialized with the API key from `config.py` and passed as `llm=` to Agent.

### 8. Prompt Caching (Anthropic)
When using Claude in CrewAI, the agent's system prompt (role + backstory) is
sent on every call. Use Anthropic's `cache_control` header to cache the system
prompt and reduce cost by ~90% on repeated calls.
Implemented in `llm_config.py` (Segment 17).

---

## Files Created in Each Agent Segment

| Segment | File | Purpose |
|---------|------|---------|
| 17 | `backend/app/agents/llm_config.py` | All LLM client instances |
| 17 | `backend/app/agents/tools/rag_tool.py` | CompanyKnowledgeBase RAG tool |
| 17 | `backend/app/agents/tools/tavily_tool.py` | Tavily web search tool |
| 17 | `backend/app/agents/base_crew.py` | Helper functions: build_agent, build_task, run_crew |
| 18 | `backend/app/agents/orchestrator.py` | Policy check agent |
| 18 | `backend/app/agents/department/marketing.py` | Marketing agent |
| 18 | `backend/app/agents/department/sales.py` | Sales agent |
| 18 | `backend/app/agents/department/development.py` | Development agent |
| 18 | `backend/app/agents/department/design.py` | Design agent |
| 18 | `backend/app/agents/department/hr.py` | HR agent |
| 18 | `backend/app/agents/department/finance.py` | Finance agent |
| 19 | `backend/app/agents/market_research.py` | Market research agent (+ Tavily) |
| 20 | `backend/app/agents/discussion.py` | Discussion round orchestration |
| 21 | `backend/app/agents/conflict_detector.py` | Conflict detection + resolution scenarios |
| 22 | `backend/app/agents/synthesizer.py` | Final report synthesis |
