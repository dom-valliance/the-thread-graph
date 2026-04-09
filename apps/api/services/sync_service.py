from __future__ import annotations

from models.sync import BookmarkSyncRequest, SessionSyncRequest, SyncResult
from repositories.sync_repository import SyncRepository


class SyncService:
    def __init__(self, repository: SyncRepository) -> None:
        self._repo = repository

    async def sync_bookmarks(
        self, bookmarks: list[BookmarkSyncRequest]
    ) -> SyncResult:
        items = [b.model_dump() for b in bookmarks]
        counts = await self._repo.upsert_bookmarks(items)
        return SyncResult(**counts)

    async def sync_sessions(
        self, sessions: list[SessionSyncRequest]
    ) -> SyncResult:
        items = [s.model_dump() for s in sessions]
        counts = await self._repo.upsert_sessions(items)
        return SyncResult(**counts)
