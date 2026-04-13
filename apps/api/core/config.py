from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve the project root .env regardless of working directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "changeme"
    auth_enabled: bool = False
    azure_ad_tenant_id: str = ""
    azure_ad_client_id: str = ""
    api_base_url: str = "http://localhost:8000"
    cors_origins: list[str] = ["http://localhost:3000"]
    anthropic_api_key: str = ""

    model_config = {"env_file": str(_ENV_FILE), "extra": "ignore"}


settings = Settings()
