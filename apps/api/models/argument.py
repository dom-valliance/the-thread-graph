from __future__ import annotations

from pydantic import BaseModel


class ArgumentResponse(BaseModel):
    id: str
    text: str
    sentiment: str
    strength: str | None = None
    speaker: str | None = None
    session_id: str | None = None
    created_at: str
    updated_at: str
