from __future__ import annotations

from pydantic import BaseModel


class SessionResponse(BaseModel):
    notion_id: str
    title: str
    date: str | None = None
    ai_suggested_viewpoint: str | None = None
    bookmark_notion_id: str | None = None
    enrichment_status: str | None = None
    created_at: str
    updated_at: str


class SessionCreate(BaseModel):
    notion_id: str
    title: str
    date: str | None = None
    ai_suggested_viewpoint: str | None = None
    bookmark_notion_id: str | None = None


class ArgumentSummary(BaseModel):
    id: str
    text: str
    sentiment: str | None = None


class ActionItemSummary(BaseModel):
    id: str
    text: str
    status: str | None = None


class ReferencedBookmark(BaseModel):
    notion_id: str
    title: str


class SessionDetail(SessionResponse):
    arguments: list[ArgumentSummary] = []
    action_items: list[ActionItemSummary] = []
    referenced_bookmarks: list[ReferencedBookmark] = []
