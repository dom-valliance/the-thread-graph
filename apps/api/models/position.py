from __future__ import annotations

from pydantic import BaseModel


class PositionResponse(BaseModel):
    id: str
    text: str
    status: str
    locked_date: str | None = None
    arc_number: int
    proposition: str | None = None
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
