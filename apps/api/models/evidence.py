from __future__ import annotations

from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    id: str
    text: str
    type: str
    source_id: str | None = None
    source_title: str | None = None
    position_id: str | None = None
    created_at: str
    updated_at: str
