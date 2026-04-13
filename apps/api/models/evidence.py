from __future__ import annotations

from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: str
    text: str
    type: str
    source_id: str | None = None
    source_title: str | None = None
    position_id: str | None = None
    proposition_mapping: str | None = None
    vault_type: str | None = None
    created_at: str
    updated_at: str


class EvidenceCreate(BaseModel):
    text: str
    type: str
    position_id: str
    source_bookmark_id: str | None = None


class EvidenceUpdate(BaseModel):
    text: str
    type: str
    source_bookmark_id: str | None = None
