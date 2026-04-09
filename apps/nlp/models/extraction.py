from __future__ import annotations

from pydantic import BaseModel, Field


class PositionRef(BaseModel):
    id: str
    text: str


class PersonRef(BaseModel):
    email: str
    name: str


class ExtractionContext(BaseModel):
    session_id: str
    arc_name: str | None = None
    existing_positions: list[PositionRef] = Field(default_factory=list)
    existing_people: list[PersonRef] = Field(default_factory=list)
    existing_topics: list[str] = Field(default_factory=list)
    existing_players: list[str] = Field(default_factory=list)


class ExtractedArgument(BaseModel):
    id: str
    text: str
    sentiment: str
    strength: str | None = None
    speaker: str | None = None
    position_id: str | None = None
    relationship_type: str


class ExtractedActionItem(BaseModel):
    id: str
    text: str
    assignee: str | None = None
    due_date: str | None = None


class ExtractedEvidence(BaseModel):
    id: str
    text: str
    type: str
    source_bookmark_id: str | None = None
    position_id: str | None = None


class ExtractedEntity(BaseModel):
    name: str
    entity_type: str  # "person" | "topic" | "player"
    matched_id: str | None = None


class ExtractionResult(BaseModel):
    arguments: list[ExtractedArgument] = Field(default_factory=list)
    action_items: list[ExtractedActionItem] = Field(default_factory=list)
    evidence: list[ExtractedEvidence] = Field(default_factory=list)
    entities: list[ExtractedEntity] = Field(default_factory=list)
