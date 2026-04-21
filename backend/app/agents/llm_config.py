from crewai import LLM
from app.config import settings

_USE_GROQ = bool(settings.GROQ_API_KEY)


def _groq(model: str = "groq/llama-3.3-70b-versatile") -> LLM:
    return LLM(model=model, api_key=settings.GROQ_API_KEY)


def _anthropic(model: str) -> LLM:
    return LLM(model=f"anthropic/{model}", api_key=settings.ANTHROPIC_API_KEY)


def _openai(model: str) -> LLM:
    return LLM(model=model, api_key=settings.OPENAI_API_KEY)


def _google(model: str) -> LLM:
    return LLM(model=f"gemini/{model}", api_key=settings.GOOGLE_API_KEY)


# Role → LLM mapping
# Set GROQ_API_KEY in .env to route all agents through Groq for testing.
# Clear it to restore the original multi-provider setup.
ORCHESTRATOR_LLM    = _groq() if _USE_GROQ else _anthropic("claude-opus-4-6")
SYNTHESIZER_LLM     = _groq() if _USE_GROQ else _anthropic("claude-opus-4-6")
DEV_LLM             = _groq() if _USE_GROQ else _anthropic("claude-sonnet-4-6")
MARKET_RESEARCH_LLM = _groq() if _USE_GROQ else _anthropic("claude-sonnet-4-6")
CONFLICT_LLM        = _groq() if _USE_GROQ else _anthropic("claude-sonnet-4-6")
MARKETING_LLM       = _groq() if _USE_GROQ else _openai("gpt-4o")
SALES_LLM           = _groq() if _USE_GROQ else _openai("gpt-4o")
FINANCE_LLM         = _groq() if _USE_GROQ else _openai("gpt-4o")
DESIGN_LLM          = _groq() if _USE_GROQ else _google("gemini-1.5-pro")
HR_LLM              = _groq() if _USE_GROQ else _google("gemini-1.5-pro")
