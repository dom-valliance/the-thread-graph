from __future__ import annotations

from pydantic import BaseModel


class CrossArcBridgeResponse(BaseModel):
    strength: str
    label: str | None = None
    source_position_id: str
    source_position_text: str
    source_arc_name: str
    source_arc_number: int
    target_position_id: str
    target_position_text: str
    target_arc_name: str
    target_arc_number: int


class UnconnectedPosition(BaseModel):
    id: str
    text: str
    arc_name: str
    arc_number: int
