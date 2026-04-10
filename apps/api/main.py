from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.config import settings
from core.database import close_driver, create_driver
from core.exceptions import register_exception_handlers
from core.middleware import setup_cors, setup_request_logging
from routers import (
    arcs,
    arguments,
    bookmarks,
    bridges,
    enrichment,
    evidence,
    health,
    objections,
    players,
    positions,
    search,
    sessions,
    sync,
    topics,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle: create and close the Neo4j driver."""
    app.state.driver = await create_driver(settings)
    yield
    await close_driver(app.state.driver)


app = FastAPI(
    title="Valliance Graph API",
    version="0.1.0",
    lifespan=lifespan,
)

setup_cors(app, settings)
setup_request_logging(app)
register_exception_handlers(app)

app.include_router(health.router, prefix="/api/v1")
app.include_router(arcs.router, prefix="/api/v1")
app.include_router(bookmarks.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(topics.router, prefix="/api/v1")
app.include_router(positions.router, prefix="/api/v1")
app.include_router(arguments.router, prefix="/api/v1")
app.include_router(evidence.router, prefix="/api/v1")
app.include_router(players.router, prefix="/api/v1")
app.include_router(objections.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(enrichment.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(bridges.router, prefix="/api/v1")
