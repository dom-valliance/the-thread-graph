from __future__ import annotations

from pydantic import BaseModel


class BriefCreate(BaseModel):
    problem_statement: str
    landscape_criteria: list[str]
    steelman_summary: str
    session_id: str
    arc_name: str


class BriefUpdate(BaseModel):
    problem_statement: str | None = None
    landscape_criteria: list[str] | None = None
    steelman_summary: str | None = None


class BriefLock(BaseModel):
    locked_by: str


class LandscapeGridEntryCreate(BaseModel):
    player_name: str
    criterion: str
    rating: str
    notes: str


class LandscapeGridEntryResponse(BaseModel):
    id: str
    player_name: str
    criterion: str
    rating: str
    notes: str


class LandscapeGridResponse(BaseModel):
    id: str
    entries: list[LandscapeGridEntryResponse] = []


class BriefResponse(BaseModel):
    id: str
    problem_statement: str
    landscape_criteria: list[str] = []
    steelman_summary: str
    status: str
    locked_date: str | None = None
    locked_by: str | None = None
    session_id: str | None = None
    arc_name: str | None = None
    landscape_grid: LandscapeGridResponse | None = None
    created_at: str
    updated_at: str
