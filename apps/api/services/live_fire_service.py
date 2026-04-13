from __future__ import annotations

from uuid import uuid4

from core.exceptions import NotFoundError, ValidationError
from models.live_fire import (
    LiveFireCreate,
    LiveFireMetricsResponse,
    LiveFirePositionMetric,
    LiveFireResponse,
)
from repositories.live_fire_repository import LiveFireRepository

VALID_OUTCOMES = {"used_successfully", "used_and_failed", "not_used"}


class LiveFireService:
    def __init__(self, repository: LiveFireRepository) -> None:
        self._repo = repository

    async def create_entry(self, data: LiveFireCreate) -> LiveFireResponse:
        if data.outcome not in VALID_OUTCOMES:
            raise ValidationError(
                f"outcome must be one of: {', '.join(sorted(VALID_OUTCOMES))}"
            )
        entry_id = str(uuid4())
        row = await self._repo.create_entry({
            "id": entry_id,
            "outcome": data.outcome,
            "context": data.context,
            "date": data.date,
            "position_id": data.position_id,
            "objection_pair_id": data.objection_pair_id,
            "reporter_email": data.reporter_email,
            "session_id": data.session_id,
        })
        if row is None:
            raise NotFoundError("Position or reporter not found")
        return LiveFireResponse(**row)

    async def list_entries(
        self,
        position_id: str | None = None,
        outcome: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[LiveFireResponse]:
        rows = await self._repo.list_entries(
            position_id=position_id,
            outcome=outcome,
            date_from=date_from,
            date_to=date_to,
        )
        return [LiveFireResponse(**row) for row in rows]

    async def get_metrics(self) -> LiveFireMetricsResponse:
        rows = await self._repo.get_metrics()
        metrics = [LiveFirePositionMetric(**row) for row in rows]
        return LiveFireMetricsResponse(metrics=metrics)
