from __future__ import annotations

from pydantic import BaseModel


class LiveFireCreate(BaseModel):
    outcome: str
    context: str
    date: str
    position_id: str
    objection_pair_id: str | None = None
    reporter_email: str
    session_id: str | None = None


class LiveFireResponse(BaseModel):
    id: str
    outcome: str
    context: str
    date: str
    position_id: str | None = None
    position_text: str | None = None
    reporter_name: str | None = None
    reporter_email: str | None = None
    created_at: str
    updated_at: str


class LiveFirePositionMetric(BaseModel):
    position_id: str
    position_text: str
    total_uses: int
    successes: int
    failures: int
    success_rate: float | None = None
    last_used: str | None = None
    never_used: bool = False


class LiveFireMetricsResponse(BaseModel):
    metrics: list[LiveFirePositionMetric]
