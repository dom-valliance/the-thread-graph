from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.bookmark import BookmarkResponse
from models.common import ApiResponse
from models.topic import TopicCoOccurrence, TopicResponse
from repositories.topic_repository import TopicRepository
from services.topic_service import TopicService

router = APIRouter(prefix="/topics", tags=["topics"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> TopicService:
    return TopicService(TopicRepository(driver))


@router.get("", response_model=ApiResponse[list[TopicResponse]])
async def list_topics(
    service: TopicService = Depends(_get_service),
) -> dict:
    """List all topics with bookmark counts."""
    topics = await service.list_topics()
    return {"data": topics, "meta": {"count": len(topics)}}


@router.get(
    "/cross-arc",
    response_model=ApiResponse[list[TopicResponse]],
)
async def get_cross_arc_topics(
    service: TopicService = Depends(_get_service),
) -> dict:
    """Get topics appearing in bookmarks that evidence positions across 3+ arcs."""
    topics = await service.get_cross_arc_topics()
    return {"data": topics, "meta": {"count": len(topics)}}


@router.get(
    "/co-occurrences",
    response_model=ApiResponse[list[TopicCoOccurrence]],
)
async def get_co_occurrences(
    service: TopicService = Depends(_get_service),
) -> dict:
    """Get topic pairs that appear on the same bookmark."""
    pairs = await service.get_co_occurrences()
    return {"data": pairs, "meta": {"count": len(pairs)}}


@router.get(
    "/{name}/bookmarks",
    response_model=ApiResponse[list[BookmarkResponse]],
)
async def get_topic_bookmarks(
    name: str,
    service: TopicService = Depends(_get_service),
) -> dict:
    """Get all bookmarks tagged with a specific topic."""
    bookmarks = await service.get_topic_bookmarks(name)
    return {"data": bookmarks, "meta": {"count": len(bookmarks)}}
