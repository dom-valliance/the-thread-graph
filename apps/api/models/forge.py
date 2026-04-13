from __future__ import annotations

from pydantic import BaseModel


class ForgeCreate(BaseModel):
    artefact_type: str
    deadline: str
    assigned_to_email: str
    session_id: str
    arc_name: str
    derived_from_id: str | None = None
    storyboard_notes: str | None = None


class ForgeUpdate(BaseModel):
    status: str | None = None
    storyboard_notes: str | None = None
    published_url: str | None = None
    editor_notes: str | None = None


class ForgeResponse(BaseModel):
    id: str
    artefact_type: str
    status: str
    deadline: str
    storyboard_notes: str | None = None
    published_url: str | None = None
    editor_notes: str | None = None
    assigned_to_name: str | None = None
    assigned_to_email: str | None = None
    editor_name: str | None = None
    editor_email: str | None = None
    session_id: str | None = None
    arc_name: str | None = None
    created_at: str
    updated_at: str


class ForgeTrackerResponse(BaseModel):
    cycle_id: str
    total_target: int = 12
    produced: int
    by_type: dict[str, int] = {}
