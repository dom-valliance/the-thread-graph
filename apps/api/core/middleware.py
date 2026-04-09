from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from core.config import Settings

logger = logging.getLogger(__name__)


def setup_cors(app: FastAPI, settings: Settings) -> None:
    """Add CORS middleware using allowed origins from settings."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_request_logging(app: FastAPI) -> None:
    """Add middleware that logs request method, path, and duration."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next: object) -> Response:
        start = time.monotonic()
        response: Response = await call_next(request)  # type: ignore[misc]
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "%s %s completed in %.1fms with status %d",
            request.method,
            request.url.path,
            duration_ms,
            response.status_code,
        )
        return response
