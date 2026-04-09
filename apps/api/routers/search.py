from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.search import SearchResult
from repositories.search_repository import SearchRepository
from services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> SearchService:
    return SearchService(SearchRepository(driver))


@router.get("", response_model=ApiResponse[list[SearchResult]])
async def search(
    q: str = Query(..., min_length=1),
    entity_types: list[str] | None = Query(default=None),
    service: SearchService = Depends(_get_service),
) -> dict:
    """Full-text search across bookmarks, positions, and arguments."""
    results = await service.search(q, entity_types)
    return {"data": results, "meta": {"count": len(results)}}
