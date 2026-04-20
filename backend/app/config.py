from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://aria:aria@localhost:5432/aria"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Supabase
    SUPABASE_JWT_SECRET: str = ""

    # Dev-mode login password (used by POST /auth/dev-login when Supabase is not configured)
    DEV_LOGIN_PASSWORD: str = "aria_dev_2025"

    # LLM keys
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "reports"

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:4000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:4000",
    ]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60


settings = Settings()
