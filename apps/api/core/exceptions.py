from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ValidationError(Exception):
    """Raised when input fails validation rules."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class ConflictError(Exception):
    """Raised when an operation conflicts with the current resource state."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class DatabaseError(Exception):
    """Raised when a database operation fails."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers returning the standard error envelope."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "NOT_FOUND", "message": exc.detail}},
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": exc.detail}},
        )

    @app.exception_handler(ConflictError)
    async def conflict_error_handler(
        request: Request, exc: ConflictError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "CONFLICT", "message": exc.detail}},
        )

    @app.exception_handler(DatabaseError)
    async def database_error_handler(
        request: Request, exc: DatabaseError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "DATABASE_ERROR", "message": exc.detail}},
        )
