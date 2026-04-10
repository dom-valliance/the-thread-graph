from __future__ import annotations

from core.exceptions import NotFoundError
from models.arc import ArcDetail, ArcResponse, ArcBridgeResponse, BookmarkEdge
from repositories.arc_repository import ArcRepository


class ArcService:
    def __init__(self, repository: ArcRepository) -> None:
        self._repo = repository

    async def list_arcs(self) -> list[ArcResponse]:
        rows = await self._repo.list_arcs()
        return [ArcResponse(**row) for row in rows]

    async def get_arc_detail(self, name: str) -> ArcDetail:
        arc = await self._repo.get_arc(name)
        if arc is None:
            raise NotFoundError(f"Arc '{name}' not found")

        bookmarks = await self._repo.get_arc_bookmarks(name)

        return ArcDetail(
            **arc,
            bookmarks=bookmarks,
        )

    async def get_arc_bookmarks_page(
        self, name: str, offset: int = 0, limit: int = 10
    ) -> tuple[list[dict], bool]:
        """Get paginated bookmarks for an arc.

        Returns (bookmarks, has_more).
        """
        arc = await self._repo.get_arc(name)
        if arc is None:
            raise NotFoundError(f"Arc '{name}' not found")

        bookmarks = await self._repo.get_arc_bookmarks_paginated(
            name, offset, limit
        )
        total = int(arc.get("bookmark_count", 0))
        has_more = offset + len(bookmarks) < total
        return bookmarks, has_more

    async def get_bookmark_edges(
        self, notion_ids: list[str]
    ) -> list[BookmarkEdge]:
        rows = await self._repo.get_bookmark_edges(notion_ids)
        return [BookmarkEdge(**row) for row in rows]

    async def get_bridges(self) -> list[ArcBridgeResponse]:
        rows = await self._repo.get_bridges()
        return [ArcBridgeResponse(**row) for row in rows]
