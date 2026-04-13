from __future__ import annotations

from pydantic import BaseModel


class CycleCreate(BaseModel):
    number: int
    start_date: str
    status: str = "upcoming"


class CycleResponse(BaseModel):
    id: str
    number: int
    start_date: str
    end_date: str
    status: str
    created_at: str
    updated_at: str


class ScheduledSessionResponse(BaseModel):
    id: str
    cycle_number: int
    week_number: int
    arc_number: int
    arc_name: str
    week_type: str
    date: str | None = None
    status: str
    lead_name: str | None = None
    lead_email: str | None = None
    shadow_name: str | None = None
    shadow_email: str | None = None
    created_at: str
    updated_at: str


class CycleCurrentResponse(BaseModel):
    id: str
    number: int
    start_date: str
    end_date: str
    status: str
    created_at: str
    updated_at: str
    current_session: ScheduledSessionResponse | None = None
    days_until_next: int | None = None


class CycleScheduleResponse(BaseModel):
    cycle: CycleResponse
    sessions: list[ScheduledSessionResponse]


class LeadShadowAssignment(BaseModel):
    lead_email: str | None = None
    shadow_email: str | None = None
