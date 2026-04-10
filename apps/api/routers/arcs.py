from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.arc import (
    ArcBridgeResponse,
    ArcDetail,
    ArcResponse,
    BookmarkEdge,
    BookmarkEdgeRequest,
)
from models.common import ApiResponse, PaginatedResponse
from repositories.arc_repository import ArcRepository
from services.arc_service import ArcService

router = APIRouter(prefix="/arcs", tags=["arcs"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ArcService:
    return ArcService(ArcRepository(driver))


@router.get("", response_model=ApiResponse[list[ArcResponse]])
async def list_arcs(service: ArcService = Depends(_get_service)) -> dict:
    """List all themes (arcs) with bookmark and session counts."""
    arcs = await service.list_arcs()
    return {"data": arcs, "meta": {"count": len(arcs)}}


@router.get("/bridges", response_model=ApiResponse[list[ArcBridgeResponse]])
async def get_bridges(service: ArcService = Depends(_get_service)) -> dict:
    """Get theme co-occurrence edges."""
    bridges = await service.get_bridges()
    return {"data": bridges, "meta": {"count": len(bridges)}}


@router.get("/{arc_name}/bookmarks", response_model=PaginatedResponse[dict])
async def get_arc_bookmarks(
    arc_name: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    service: ArcService = Depends(_get_service),
) -> dict:
    """Get paginated bookmarks for an arc."""
    bookmarks, has_more = await service.get_arc_bookmarks_page(
        arc_name, offset, limit
    )
    return {
        "data": bookmarks,
        "meta": {
            "count": len(bookmarks),
            "cursor": None,
            "has_more": has_more,
        },
    }


@router.post(
    "/{arc_name}/bookmarks/edges",
    response_model=ApiResponse[list[BookmarkEdge]],
)
async def get_arc_bookmark_edges(
    arc_name: str,
    body: BookmarkEdgeRequest,
    service: ArcService = Depends(_get_service),
) -> dict:
    """Get bookmark-to-bookmark edges based on shared topics."""
    edges = await service.get_bookmark_edges(body.notion_ids)
    return {"data": edges, "meta": {"count": len(edges)}}


@router.get("/{arc_name}", response_model=ApiResponse[ArcDetail])
async def get_arc(
    arc_name: str,
    service: ArcService = Depends(_get_service),
) -> dict:
    """Get theme detail with associated bookmarks."""
    detail = await service.get_arc_detail(arc_name)
    return {"data": detail}
