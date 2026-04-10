from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import NotFoundError
from models.arc import ArcDetail, ArcResponse, ArcBridgeResponse, BookmarkEdge
from repositories.arc_repository import ArcRepository
from services.arc_service import ArcService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_repo() -> MagicMock:
    """Return a fully-mocked ArcRepository."""
    return MagicMock(spec=ArcRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> ArcService:
    return ArcService(mock_repo)


# ---------------------------------------------------------------------------
# Sample data helpers
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
    "source_arc_name": "AI Governance",
    "target_arc_name": "Ethics",
    "shared_topics": 3,
}


# ---------------------------------------------------------------------------
# Tests: list_arcs
# ---------------------------------------------------------------------------


async def test_list_arcs_returns_arc_response_objects(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """list_arcs returns a list of ArcResponse models."""
    mock_repo.list_arcs = AsyncMock(return_value=[_ARC_ROW])

    result = await service.list_arcs()

    assert len(result) == 1
    assert isinstance(result[0], ArcResponse)
    assert result[0].name == "AI Governance"
    assert result[0].bookmark_count == 5
    mock_repo.list_arcs.assert_awaited_once()


async def test_list_arcs_returns_empty_list_when_no_arcs(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """list_arcs returns an empty list when the repository has no themes."""
    mock_repo.list_arcs = AsyncMock(return_value=[])

    result = await service.list_arcs()

    assert result == []


# ---------------------------------------------------------------------------
# Tests: get_arc_detail
# ---------------------------------------------------------------------------


async def test_get_arc_detail_raises_not_found_when_arc_missing(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_arc_detail raises NotFoundError when the theme does not exist."""
    mock_repo.get_arc = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError, match="not found"):
        await service.get_arc_detail("Nonexistent")


async def test_get_arc_detail_returns_arc_with_bookmarks(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_arc_detail returns an ArcDetail populated with bookmarks."""
    mock_repo.get_arc = AsyncMock(return_value=_ARC_BASE)
    mock_repo.get_arc_bookmarks = AsyncMock(return_value=[{"notion_id": "bk-1", "title": "Test"}])

    result = await service.get_arc_detail("AI Governance")

    assert isinstance(result, ArcDetail)
    assert result.name == "AI Governance"
    assert len(result.bookmarks) == 1


# ---------------------------------------------------------------------------
# Tests: get_bridges
# ---------------------------------------------------------------------------


async def test_get_bridges_returns_theme_bridge_response_objects(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_bridges returns a list of ArcBridgeResponse models."""
    mock_repo.get_bridges = AsyncMock(return_value=[_BRIDGE_ROW])

    result = await service.get_bridges()

    assert len(result) == 1
    assert isinstance(result[0], ArcBridgeResponse)
    assert result[0].source_arc_name == "AI Governance"
    assert result[0].shared_topics == 3


# ---------------------------------------------------------------------------
# Tests: get_arc_bookmarks_page
# ---------------------------------------------------------------------------


async def test_get_arc_bookmarks_page_returns_bookmarks_and_has_more(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_arc_bookmarks_page returns paginated bookmarks with has_more flag."""
    mock_repo.get_arc = AsyncMock(return_value=_ARC_BASE)
    mock_repo.get_arc_bookmarks_paginated = AsyncMock(
        return_value=[{"notion_id": f"bk-{i}"} for i in range(10)]
    )

    bookmarks, has_more = await service.get_arc_bookmarks_page(
        "AI Governance", offset=0, limit=10
    )

    assert len(bookmarks) == 10
    # bookmark_count is 5 in _ARC_BASE but we returned 10 items from offset 0
    # so 0 + 10 >= 5 => has_more is False
    assert has_more is False
    mock_repo.get_arc_bookmarks_paginated.assert_awaited_once_with(
        "AI Governance", 0, 10
    )


async def test_get_arc_bookmarks_page_has_more_when_more_exist(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """has_more is True when offset + page size < total bookmark count."""
    arc_with_many = {**_ARC_BASE, "bookmark_count": 25}
    mock_repo.get_arc = AsyncMock(return_value=arc_with_many)
    mock_repo.get_arc_bookmarks_paginated = AsyncMock(
        return_value=[{"notion_id": f"bk-{i}"} for i in range(10)]
    )

    bookmarks, has_more = await service.get_arc_bookmarks_page(
        "AI Governance", offset=0, limit=10
    )

    assert len(bookmarks) == 10
    assert has_more is True


async def test_get_arc_bookmarks_page_raises_not_found(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_arc_bookmarks_page raises NotFoundError when arc does not exist."""
    mock_repo.get_arc = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError, match="not found"):
        await service.get_arc_bookmarks_page("Nonexistent", 0, 10)


# ---------------------------------------------------------------------------
# Tests: get_bookmark_edges
# ---------------------------------------------------------------------------


_EDGE_ROW = {
    "source_notion_id": "bk-1",
    "target_notion_id": "bk-2",
    "shared_topics": 2,
    "shared_topic_names": ["AI", "Ethics"],
}


async def test_get_bookmark_edges_returns_edge_objects(
    service: ArcService, mock_repo: MagicMock
) -> None:
    """get_bookmark_edges returns a list of BookmarkEdge models."""
    mock_repo.get_bookmark_edges = AsyncMock(return_value=[_EDGE_ROW])

    result = await service.get_bookmark_edges(["bk-1", "bk-2"])

    assert len(result) == 1
    assert isinstance(result[0], BookmarkEdge)
    assert result[0].source_notion_id == "bk-1"
    assert result[0].shared_topics == 2
    assert result[0].shared_topic_names == ["AI", "Ethics"]
