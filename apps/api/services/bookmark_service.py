from __future__ import annotations

from core.exceptions import NotFoundError
from models.bookmark import (
    BookmarkDetail,
    BookmarkResponse,
    RelatedPosition,
    RelatedSession,
)
from repositories.bookmark_repository import BookmarkRepository


class BookmarkService:
    def __init__(self, repository: BookmarkRepository) -> None:
        self._repo = repository

    async def list_bookmarks(
        self,
        topic: str | None = None,
        theme: str | None = None,
        edge_or_foundational: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[BookmarkResponse]:
        rows = await self._repo.list_bookmarks(
            topic=topic,
            theme=theme,
            edge_or_foundational=edge_or_foundational,
            cursor=cursor,
            limit=limit,
        )
        return [BookmarkResponse(**row) for row in rows]

    async def get_bookmark_detail(self, notion_id: str) -> BookmarkDetail:
        row = await self._repo.get_bookmark(notion_id)
        if row is None:
            raise NotFoundError(f"Bookmark '{notion_id}' not found")

        # Filter out empty relationship entries produced by OPTIONAL MATCH
        positions = [
            RelatedPosition(**p)
            for p in row.pop("related_positions", [])
            if p.get("id") is not None
        ]
        sessions = [
            RelatedSession(**s)
            for s in row.pop("related_sessions", [])
            if s.get("notion_id") is not None
        ]

        return BookmarkDetail(
            **row,
            related_positions=positions,
            related_sessions=sessions,
        )

    async def get_high_connectivity_bookmarks(self) -> list[BookmarkResponse]:
        rows = await self._repo.get_high_connectivity_bookmarks()
        return [BookmarkResponse(**row) for row in rows]

    async def upsert_bookmarks(self, bookmarks: list[dict[str, object]]) -> int:
        return await self._repo.upsert_bookmarks(bookmarks)
