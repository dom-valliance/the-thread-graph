from __future__ import annotations

from datetime import date, timedelta

from core.exceptions import NotFoundError, ValidationError
from models.cycle import (
    CycleCreate,
    CycleCurrentResponse,
    CycleResponse,
    CycleScheduleResponse,
    ScheduledSessionResponse,
)
from repositories.cycle_repository import CycleRepository

WEEKS_PER_CYCLE = 12
WEEKS_PER_ARC = 2


class CycleService:
    def __init__(self, repository: CycleRepository) -> None:
        self._repo = repository

    async def list_cycles(self) -> list[CycleResponse]:
        rows = await self._repo.list_cycles()
        return [CycleResponse(**row) for row in rows]

    async def get_current_cycle(self) -> CycleCurrentResponse:
        row = await self._repo.get_current_cycle()
        if row is None:
            raise NotFoundError("No active cycle found")
        return CycleCurrentResponse(**row)

    async def create_cycle(self, data: CycleCreate) -> CycleResponse:
        if data.number < 1:
            raise ValidationError("Cycle number must be at least 1")

        cycle_id = f"cycle-{data.number}"
        start = date.fromisoformat(data.start_date)
        end = start + timedelta(weeks=WEEKS_PER_CYCLE - 1)

        sessions: list[dict[str, object]] = []
        for week in range(1, WEEKS_PER_CYCLE + 1):
            arc_number = (week - 1) // WEEKS_PER_ARC + 1
            week_in_arc = (week - 1) % WEEKS_PER_ARC
            week_type = "problem_landscape" if week_in_arc == 0 else "position_pitch"
            session_date = start + timedelta(weeks=week - 1)

            sessions.append({
                "id": f"ss-c{data.number}-w{week}",
                "cycle_number": data.number,
                "week_number": week,
                "arc_number": arc_number,
                "week_type": week_type,
                "date": session_date.isoformat(),
            })

        row = await self._repo.create_cycle(
            cycle_id=cycle_id,
            number=data.number,
            start_date=data.start_date,
            end_date=end.isoformat(),
            status=data.status,
            sessions=sessions,
        )
        if row is None:
            raise NotFoundError("Failed to create cycle")
        return CycleResponse(**row)

    async def get_cycle_schedule(self, cycle_id: str) -> CycleScheduleResponse:
        cycle_row, session_rows = await self._repo.get_cycle_schedule(cycle_id)
        if cycle_row is None:
            raise NotFoundError(f"Cycle '{cycle_id}' not found")
        return CycleScheduleResponse(
            cycle=CycleResponse(**cycle_row),
            sessions=[ScheduledSessionResponse(**s) for s in session_rows],
        )

    async def update_session_assignment(
        self,
        session_id: str,
        lead_email: str | None,
        shadow_email: str | None,
    ) -> ScheduledSessionResponse:
        row = await self._repo.update_session_assignment(
            session_id, lead_email, shadow_email
        )
        if row is None:
            raise NotFoundError(f"Scheduled session '{session_id}' not found")
        return ScheduledSessionResponse(**row)

    async def get_scheduled_session(
        self, session_id: str
    ) -> ScheduledSessionResponse:
        row = await self._repo.get_scheduled_session(session_id)
        if row is None:
            raise NotFoundError(f"Scheduled session '{session_id}' not found")
        return ScheduledSessionResponse(**row)
