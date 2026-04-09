from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.bookmark import BookmarkDetail, BookmarkResponse
from models.common import ApiResponse
from repositories.bookmark_repository import BookmarkRepository
from services.bookmark_service import BookmarkService

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> BookmarkService:
    return BookmarkService(BookmarkRepository(driver))


@router.get("", response_model=ApiResponse[list[BookmarkResponse]])
async def list_bookmarks(
    topic: str | None = Query(None, description="Filter by topic name"),
    theme: str | None = Query(None, description="Filter by theme name"),
    edge_or_foundational: str | None = Query(
        None, description="Filter by edge or foundational classification"
    ),
    cursor: str | None = Query(None, description="Cursor for pagination"),
    limit: int = Query(25, ge=1, le=100, description="Page size"),
    service: BookmarkService = Depends(_get_service),
) -> dict:
    """List bookmarks with optional filters and cursor-based pagination."""
    bookmarks = await service.list_bookmarks(
        topic=topic,
        theme=theme,
        edge_or_foundational=edge_or_foundational,
        cursor=cursor,
        limit=limit,
    )
    return {"data": bookmarks, "meta": {"count": len(bookmarks)}}


@router.get(
    "/high-connectivity",
    response_model=ApiResponse[list[BookmarkResponse]],
)
async def get_high_connectivity_bookmarks(
    service: BookmarkService = Depends(_get_service),
) -> dict:
    """Get bookmarks that evidence positions across multiple arcs."""
    bookmarks = await service.get_high_connectivity_bookmarks()
    return {"data": bookmarks, "meta": {"count": len(bookmarks)}}


@router.get("/{notion_id}", response_model=ApiResponse[BookmarkDetail])
async def get_bookmark(
    notion_id: str,
    service: BookmarkService = Depends(_get_service),
) -> dict:
    """Get a single bookmark with all relationships."""
    detail = await service.get_bookmark_detail(notion_id)
    return {"data": detail}
