from __future__ import annotations

from core.exceptions import NotFoundError
from models.arc import ArcDetail, ArcResponse, ThemeBridgeResponse
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
            raise NotFoundError(f"Theme '{name}' not found")

        bookmarks = await self._repo.get_arc_bookmarks(name)

        return ArcDetail(
            **arc,
            bookmarks=bookmarks,
        )

    async def get_bridges(self) -> list[ThemeBridgeResponse]:
        rows = await self._repo.get_bridges()
        return [ThemeBridgeResponse(**row) for row in rows]
