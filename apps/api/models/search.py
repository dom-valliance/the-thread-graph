from __future__ import annotations

from pydantic import BaseModel


class SearchResult(BaseModel):
    entity_type: str
    id: str
    title: str
    snippet: str
    score: float


class SearchQuery(BaseModel):
    q: str
    entity_types: list[str] | None = None
