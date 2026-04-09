from __future__ import annotations

from pydantic import BaseModel


class PlayerResponse(BaseModel):
    name: str
    bookmark_count: int = 0
    created_at: str
    updated_at: str


class PlayerBookmarkResponse(BaseModel):
    id: str
    title: str
    source: str | None = None
    url: str | None = None
    ai_summary: str | None = None
    created_at: str
    updated_at: str
