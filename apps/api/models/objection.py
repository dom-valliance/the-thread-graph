from __future__ import annotations

from pydantic import BaseModel


class ObjectionResponsePairResponse(BaseModel):
    id: str
    objection_text: str
    response_text: str
    position_id: str | None = None
    created_at: str
    updated_at: str
