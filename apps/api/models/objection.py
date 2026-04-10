from __future__ import annotations

from pydantic import BaseModel


class ObjectionResponsePairResponse(BaseModel):
    id: str
    objection_text: str
    response_text: str
    position_id: str | None = None
    created_at: str
    updated_at: str


class ObjectionPairWithContext(BaseModel):
    id: str
    objection_text: str
    response_text: str
    position_id: str
    position_text: str
    arc_name: str
    arc_number: int
    created_at: str
    updated_at: str


class ObjectionPairCreate(BaseModel):
    objection_text: str
    response_text: str
    position_id: str


class ObjectionPairUpdate(BaseModel):
    objection_text: str
    response_text: str
