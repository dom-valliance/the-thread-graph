from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.sync import BookmarkSyncRequest, SessionSyncRequest, SyncResult
from repositories.sync_repository import SyncRepository
from services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["sync"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> SyncService:
    return SyncService(SyncRepository(driver))


@router.post("/bookmarks", response_model=ApiResponse[SyncResult])
async def sync_bookmarks(
    bookmarks: list[BookmarkSyncRequest],
    service: SyncService = Depends(_get_service),
) -> dict:
    """Upsert bookmarks from Notion sync, creating topic and theme relationships."""
    result = await service.sync_bookmarks(bookmarks)
    return {"data": result}


@router.post("/sessions", response_model=ApiResponse[SyncResult])
async def sync_sessions(
    sessions: list[SessionSyncRequest],
    service: SyncService = Depends(_get_service),
) -> dict:
    """Upsert sessions from Notion sync, creating arc relationships."""
    result = await service.sync_sessions(sessions)
    return {"data": result}
