from __future__ import annotations

from neo4j import AsyncGraphDatabase, AsyncDriver, NotificationDisabledCategory

from core.config import Settings


async def create_driver(settings: Settings) -> AsyncDriver:
    """Create an async Neo4j driver from application settings."""
    return AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        notifications_disabled_categories=[NotificationDisabledCategory.UNRECOGNIZED],
    )


async def close_driver(driver: AsyncDriver) -> None:
    """Gracefully close the Neo4j driver, releasing all connections."""
    await driver.close()
