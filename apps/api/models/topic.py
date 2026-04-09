from __future__ import annotations

from pydantic import BaseModel


class TopicResponse(BaseModel):
    name: str
    bookmark_count: int = 0
    primary_theme: str | None = None
    created_at: str
    updated_at: str


class TopicCoOccurrence(BaseModel):
    name: str
    co_occurring_topic: str
    count: int
