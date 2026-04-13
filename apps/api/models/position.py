from __future__ import annotations

from pydantic import BaseModel


class PositionCreate(BaseModel):
    text: str
    arc_number: int
    session_id: str
    anti_position_text: str | None = None
    cross_arc_bridge_text: str | None = None
    p1_v1_mapping: str | None = None


class PositionUpdate(BaseModel):
    text: str | None = None
    anti_position_text: str | None = None
    cross_arc_bridge_text: str | None = None
    p1_v1_mapping: str | None = None
    steelman_addressed: str | None = None


class PositionLock(BaseModel):
    locked_by: str


class PositionRevise(BaseModel):
    trigger_type: str
    trigger_id: str


class PositionResponse(BaseModel):
    id: str
    text: str
    status: str
    version: int = 1
    locked_date: str | None = None
    locked_by: str | None = None
    arc_number: int
    proposition: str | None = None
    anti_position_text: str | None = None
    cross_arc_bridge_text: str | None = None
    p1_v1_mapping: str | None = None
    steelman_addressed: str | None = None
    created_at: str
    updated_at: str


class PositionVersionResponse(BaseModel):
    id: str
    text: str
    version: int
    status: str
    locked_date: str | None = None
    locked_by: str | None = None
    created_at: str
    updated_at: str


class AntiPositionResponse(BaseModel):
    id: str
    text: str
    position_id: str
    created_at: str
    updated_at: str


class EvidenceChainItem(BaseModel):
    id: str
    text: str
    type: str
    source_title: str | None = None


class ArgumentSummary(BaseModel):
    id: str
    text: str
    sentiment: str
    strength: str | None = None
    speaker: str | None = None
    source_session_id: str | None = None


class PositionDetail(PositionResponse):
    anti_position: AntiPositionResponse | None = None
    evidence_chain: list[EvidenceChainItem]
    supporting_arguments: list[ArgumentSummary]
    challenging_arguments: list[ArgumentSummary]


class SteelmanItem(BaseModel):
    id: str
    text: str


class ObjectionPair(BaseModel):
    id: str
    objection_text: str
    response_text: str


class ArgumentMapResponse(BaseModel):
    position: PositionResponse
    supporting: list[ArgumentSummary]
    challenging: list[ArgumentSummary]
    steelman: list[SteelmanItem]
    objection_pairs: list[ObjectionPair]


class EvidenceTrailBookmark(BaseModel):
    notion_id: str
    title: str
    url: str | None = None
    source: str | None = None
    edge_or_foundational: str | None = None
    ai_summary: str | None = None
    arc_names: list[str] = []


class EvidenceTrailItem(BaseModel):
    id: str
    text: str
    type: str
    source_bookmark: EvidenceTrailBookmark | None = None


class EvidenceTrailResponse(BaseModel):
    position_id: str
    position_text: str
    evidence: list[EvidenceTrailItem]
    unsourced_count: int
    bridge_bookmark_count: int
