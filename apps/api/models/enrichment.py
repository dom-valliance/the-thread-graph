from __future__ import annotations

from pydantic import BaseModel


class ArgumentCreate(BaseModel):
    id: str
    text: str
    sentiment: str
    strength: str | None = None
    speaker: str | None = None
    session_id: str | None = None
    position_id: str | None = None
    relationship_type: str  # "supports" or "challenges"


class ActionItemCreate(BaseModel):
    id: str
    text: str
    assignee: str | None = None
    due_date: str | None = None
    session_id: str | None = None


class EvidenceCreate(BaseModel):
    id: str
    text: str
    type: str
    source_bookmark_id: str | None = None
    position_id: str | None = None


class EnrichmentResult(BaseModel):
    created_count: int
    updated_count: int
