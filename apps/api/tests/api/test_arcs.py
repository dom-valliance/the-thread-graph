from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

_ARC_ROW = {
    "name": "AI Governance",
    "bookmark_count": 5,
    "session_count": 2,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-02T00:00:00Z",
}

_ARC_BASE = {
    "name": "AI Governance",
    "bookmark_count": 5,
    "session_count": 2,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-02T00:00:00Z",
}

_BRIDGE_ROW = {
    "source_theme_name": "AI Governance",
    "target_theme_name": "Ethics",
    "shared_topics": 3,
}

_REPO_PATH = "routers.arcs.ArcRepository"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _patch_repo(**method_returns):
    """Patch ArcRepository methods used by the router's dependency chain."""
    instance = AsyncMock()
    for method, value in method_returns.items():
        getattr(instance, method).return_value = value
    mock_cls = MagicMock(return_value=instance)
    return patch(_REPO_PATH, mock_cls)


# ---------------------------------------------------------------------------
# Tests: GET /api/v1/arcs
# ---------------------------------------------------------------------------


async def test_list_arcs_returns_200_with_envelope(
    client: httpx.AsyncClient,
) -> None:
    """GET /api/v1/arcs returns 200 with data list and meta count."""
    with _patch_repo(list_arcs=[_ARC_ROW]):
        resp = await client.get("/api/v1/arcs")

    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "meta" in body
    assert body["meta"]["count"] == 1
    assert body["data"][0]["name"] == "AI Governance"
    assert body["data"][0]["bookmark_count"] == 5


async def test_list_arcs_returns_empty_list_when_no_arcs(
    client: httpx.AsyncClient,
) -> None:
    """GET /api/v1/arcs returns an empty data list when no themes exist."""
    with _patch_repo(list_arcs=[]):
        resp = await client.get("/api/v1/arcs")

    assert resp.status_code == 200
    assert resp.json()["data"] == []
    assert resp.json()["meta"]["count"] == 0


# ---------------------------------------------------------------------------
# Tests: GET /api/v1/arcs/{arc_name}
# ---------------------------------------------------------------------------


async def test_get_arc_returns_200_with_detail(
    client: httpx.AsyncClient,
) -> None:
    """GET /api/v1/arcs/AI%20Governance returns 200 with theme detail."""
    with _patch_repo(get_arc=_ARC_BASE, get_arc_bookmarks=[]):
        resp = await client.get("/api/v1/arcs/AI%20Governance")

    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["name"] == "AI Governance"


async def test_get_arc_returns_404_when_arc_missing(
    client: httpx.AsyncClient,
) -> None:
    """GET /api/v1/arcs/Nonexistent returns 404 with the standard error envelope."""
    with _patch_repo(get_arc=None):
        resp = await client.get("/api/v1/arcs/Nonexistent")

    assert resp.status_code == 404
    body = resp.json()
    assert body["error"]["code"] == "NOT_FOUND"


# ---------------------------------------------------------------------------
# Tests: GET /api/v1/arcs/bridges
# ---------------------------------------------------------------------------


async def test_get_bridges_returns_200(
    client: httpx.AsyncClient,
) -> None:
    """GET /api/v1/arcs/bridges returns 200 with theme bridges."""
    with _patch_repo(get_bridges=[_BRIDGE_ROW]):
        resp = await client.get("/api/v1/arcs/bridges")

    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["count"] == 1
    assert body["data"][0]["source_theme_name"] == "AI Governance"
    assert body["data"][0]["shared_topics"] == 3
