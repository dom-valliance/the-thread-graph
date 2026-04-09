from __future__ import annotations

from models.search import SearchResult
from repositories.search_repository import SearchRepository


class SearchService:
    def __init__(self, repository: SearchRepository) -> None:
        self._repo = repository

    async def search(
        self,
        query_text: str,
        entity_types: list[str] | None = None,
    ) -> list[SearchResult]:
        rows = await self._repo.search(query_text, entity_types)
        return [SearchResult(**row) for row in rows]
