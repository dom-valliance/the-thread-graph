from __future__ import annotations

from pydantic import BaseModel


class BookmarkResponse(BaseModel):
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
    created_at: str
    updated_at: str


class BookmarkCreate(BaseModel):
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


class RelatedPosition(BaseModel):
    id: str
    text: str


class RelatedSession(BaseModel):
    notion_id: str
    title: str


class BookmarkDetail(BookmarkResponse):
    related_positions: list[RelatedPosition] = []
    related_sessions: list[RelatedSession] = []
