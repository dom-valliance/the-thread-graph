from __future__ import annotations

from pydantic import BaseModel


class ArcResponse(BaseModel):
    name: str
    bookmark_count: int = 0
    session_count: int = 0
    created_at: str
    updated_at: str


class ThemeBridgeResponse(BaseModel):
    source_theme_name: str
    target_theme_name: str
    shared_topics: int


class ArcDetail(BaseModel):
    name: str
    bookmark_count: int = 0
    session_count: int = 0
    bookmarks: list[dict] = []
    created_at: str
    updated_at: str
