"""Application configuration."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Office Studio"
    debug: bool = False
    secret_key: str = "change-me-in-production-use-openssl-rand-hex-32"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_days: int = 30

    database_url: str = "sqlite:///./office_studio.db"
    upload_dir: Path = Path("./uploads")
    max_upload_mb: int = 100
    max_uncompressed_mb: int = 500

    cors_origins: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
    ]

    # AI
    ai_provider: str = "none"  # openai | anthropic | ollama | none
    ai_api_key: str | None = None
    ai_model: str = "gpt-4o-mini"
    ai_base_url: str | None = None

    # Collaboration
    collab_enabled: bool = True

    # Feature flags
    enable_ai: bool = True
    enable_collab: bool = True
    enable_admin: bool = True

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def max_uncompressed_bytes(self) -> int:
        return self.max_uncompressed_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
