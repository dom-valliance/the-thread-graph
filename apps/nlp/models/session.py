from __future__ import annotations

from pydantic import BaseModel


class SessionInput(BaseModel):
    notion_id: str
    title: str
    transcript: str
    theme_name: str | None = None
    summary: str | None = None
