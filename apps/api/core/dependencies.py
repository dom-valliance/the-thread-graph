from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from neo4j import AsyncDriver

from core.config import Settings, settings


async def get_driver(request: Request) -> AsyncGenerator[AsyncDriver, None]:
    """Yield the Neo4j async driver from application state."""
    driver: AsyncDriver = request.app.state.driver
    yield driver


def get_settings() -> Settings:
    """Return the application settings instance."""
    return settings
