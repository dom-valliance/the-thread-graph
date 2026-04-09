from __future__ import annotations

from pydantic import BaseModel


class BookmarkNode(BaseModel):
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
    created_at: str
    updated_at: str


class SessionNode(BaseModel):
    notion_id: str
    title: str
    date: str | None = None
    duration: int | None = None
    summary: str | None = None
    transcript: str | None = None
    theme_name: str | None = None
    enrichment_status: str | None = None
    created_at: str
    updated_at: str


class PositionNode(BaseModel):
    id: str
    text: str
    status: str
    locked_date: str | None = None
    arc_number: int
    created_at: str
    updated_at: str


class AntiPositionNode(BaseModel):
    id: str
    text: str
    position_id: str
    created_at: str
    updated_at: str


class PersonNode(BaseModel):
    email: str
    name: str
    created_at: str
    updated_at: str


class TopicNode(BaseModel):
    name: str
    created_at: str
    updated_at: str


class ThemeNode(BaseModel):
    name: str
    created_at: str
    updated_at: str


class ArgumentNode(BaseModel):
    id: str
    text: str
    sentiment: str
    strength: str | None = None
    speaker: str | None = None
    session_id: str | None = None
    created_at: str
    updated_at: str


class ActionItemNode(BaseModel):
    id: str
    text: str
    assignee: str | None = None
    due_date: str | None = None
    status: str
    created_at: str
    updated_at: str


class ObjectionResponsePairNode(BaseModel):
    id: str
    objection_text: str
    response_text: str
    position_id: str
    created_at: str
    updated_at: str


class CrossArcBridgeNode(BaseModel):
    id: str
    label: str | None = None
    strength: str
    source_position_id: str
    target_position_id: str
    created_at: str
    updated_at: str


class SteelmanArgumentNode(BaseModel):
    id: str
    text: str
    arc_number: int
    created_at: str
    updated_at: str


class EvidenceNode(BaseModel):
    id: str
    text: str
    type: str
    source_id: str | None = None
    created_at: str
    updated_at: str


class PlayerNode(BaseModel):
    name: str
    created_at: str
    updated_at: str


class PropositionNode(BaseModel):
    name: str
    created_at: str
    updated_at: str
