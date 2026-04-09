from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from fastapi import FastAPI
from neo4j import AsyncDriver

from core.dependencies import get_driver
from core.exceptions import register_exception_handlers
from routers.arcs import router as arcs_router
from routers.health import router as health_router


@pytest.fixture()
def mock_driver() -> MagicMock:
    """Create a MagicMock standing in for the Neo4j AsyncDriver."""
    driver = MagicMock(spec=AsyncDriver)
    driver.session = MagicMock(return_value=AsyncMock())
    return driver


@pytest.fixture()
def test_app(mock_driver: MagicMock) -> FastAPI:
    """Build a FastAPI app with the driver dependency overridden."""
    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(arcs_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/api/v1")

    async def _override_driver():
        yield mock_driver

    app.dependency_overrides[get_driver] = _override_driver
    return app


@pytest.fixture()
async def client(test_app: FastAPI) -> httpx.AsyncClient:
    """Provide an async HTTP client bound to the test application."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=test_app),
        base_url="http://test",
    ) as ac:
        yield ac
