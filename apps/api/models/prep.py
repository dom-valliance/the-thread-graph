from __future__ import annotations

from pydantic import BaseModel


class WorkshopAssignmentCreate(BaseModel):
    player_or_approach: str
    assigned_to_email: str


class WorkshopAssignmentUpdate(BaseModel):
    status: str | None = None
    analysis_notes: str | None = None


class WorkshopAssignmentResponse(BaseModel):
    id: str
    player_or_approach: str
    analysis_notes: str | None = None
    status: str
    assigned_to_name: str | None = None
    assigned_to_email: str | None = None
    player_name: str | None = None
    created_at: str
    updated_at: str


class ReadingAssignmentCreate(BaseModel):
    bookmark_notion_id: str
    assigned_to_email: str


class ReadingAssignmentUpdate(BaseModel):
    status: str


class ReadingAssignmentResponse(BaseModel):
    id: str
    status: str
    assigned_to_name: str | None = None
    assigned_to_email: str | None = None
    bookmark_title: str | None = None
    bookmark_notion_id: str | None = None
    created_at: str
    updated_at: str


class PrepBriefBookmark(BaseModel):
    notion_id: str
    title: str
    url: str | None = None
    date_added: str | None = None


class PrepBriefResponse(BaseModel):
    session_id: str
    arc_name: str | None = None
    recent_bookmarks: list[PrepBriefBookmark] = []
    previous_locked_position_text: str | None = None
    evidence_count: int = 0
