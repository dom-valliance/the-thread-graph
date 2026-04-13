from __future__ import annotations

from pydantic import BaseModel


class FlashCreate(BaseModel):
    title: str
    description: str
    position_id: str
    raised_by_email: str


class FlashUpdate(BaseModel):
    status: str | None = None
    reviewed_date: str | None = None


class FlashResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    reviewed_date: str | None = None
    position_id: str | None = None
    position_text: str | None = None
    raised_by_name: str | None = None
    raised_by_email: str | None = None
    created_at: str
    updated_at: str
