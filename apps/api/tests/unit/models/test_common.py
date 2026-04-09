from __future__ import annotations

from models.common import (
    ApiResponse,
    ErrorDetail,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
)


def test_api_response_serialises_with_data_field() -> None:
    """ApiResponse serialises its payload under the 'data' key."""
    resp = ApiResponse(data={"name": "Arc One"})
    body = resp.model_dump()

    assert body["data"] == {"name": "Arc One"}
    assert body["meta"] is None


def test_api_response_serialises_with_meta() -> None:
    """ApiResponse includes meta when provided."""
    resp = ApiResponse(data=[], meta={"count": 3})
    body = resp.model_dump()

    assert body["meta"] == {"count": 3}


def test_paginated_response_includes_pagination_meta() -> None:
    """PaginatedResponse carries a PaginationMeta with count, cursor, and has_more."""
    meta = PaginationMeta(count=2, cursor="abc123", has_more=True)
    resp = PaginatedResponse(data=["a", "b"], meta=meta)
    body = resp.model_dump()

    assert body["data"] == ["a", "b"]
    assert body["meta"]["count"] == 2
    assert body["meta"]["cursor"] == "abc123"
    assert body["meta"]["has_more"] is True


def test_paginated_response_cursor_defaults_to_none() -> None:
    """PaginationMeta defaults cursor to None when omitted."""
    meta = PaginationMeta(count=0, has_more=False)

    assert meta.cursor is None


def test_error_response_serialises_code_and_message() -> None:
    """ErrorResponse contains a nested error object with code and message."""
    resp = ErrorResponse(
        error=ErrorDetail(code="NOT_FOUND", message="Arc 42 not found")
    )
    body = resp.model_dump()

    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Arc 42 not found"
