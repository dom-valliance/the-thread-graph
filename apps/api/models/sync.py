from __future__ import annotations

from pydantic import BaseModel


class BookmarkSyncRequest(BaseModel):
    notion_id: str
    title: str
    source: str | None = None
    url: str | None = None
    ai_summary: str | None = None
    valliance_viewpoint: str | None = None
    edge_or_foundational: str | None = None
    focus: str | None = None
    time_consumption: str | None = None
    date_added: str | None = None
    topic_names: list[str] = []
    theme_name: str | None = None
    arc_bucket_names: list[str] = []


class SessionSyncRequest(BaseModel):
    notion_id: str
    title: str
    date: str | None = None
    duration: int | None = None
    summary: str | None = None
    transcript: str | None = None
    theme_name: str | None = None


class SyncResult(BaseModel):
    created_count: int
    updated_count: int
