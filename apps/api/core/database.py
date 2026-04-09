from __future__ import annotations

from neo4j import AsyncGraphDatabase
from neo4j import AsyncDriver

from core.config import Settings


async def create_driver(settings: Settings) -> AsyncDriver:
    """Create an async Neo4j driver from application settings."""
    return AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


async def close_driver(driver: AsyncDriver) -> None:
    """Gracefully close the Neo4j driver, releasing all connections."""
    await driver.close()
