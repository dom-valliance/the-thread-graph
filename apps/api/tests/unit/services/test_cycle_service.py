from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import NotFoundError, ValidationError
from models.cycle import CycleCreate, CycleResponse, CycleScheduleResponse, ScheduledSessionResponse
from repositories.cycle_repository import CycleRepository
from services.cycle_service import CycleService


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock(spec=CycleRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> CycleService:
    return CycleService(mock_repo)


_CYCLE_ROW = {
    "id": "cycle-1",
    "number": 1,
    "start_date": "2026-04-10",
    "end_date": "2026-06-26",
    "status": "active",
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}

_SESSION_ROW = {
    "id": "ss-c1-w1",
    "cycle_number": 1,
    "week_number": 1,
    "arc_number": 1,
    "arc_name": "Agentic AI",
    "week_type": "problem_landscape",
    "date": "2026-04-10",
    "status": "upcoming",
    "lead_name": None,
    "lead_email": None,
    "shadow_name": None,
    "shadow_email": None,
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}


async def test_create_cycle_generates_12_sessions(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Creating a cycle passes 12 session dicts to the repository."""
    mock_repo.create_cycle = AsyncMock(return_value=_CYCLE_ROW)

    data = CycleCreate(number=1, start_date="2026-04-10", status="active")
    result = await service.create_cycle(data)

    assert isinstance(result, CycleResponse)
    assert result.id == "cycle-1"

    call_kwargs = mock_repo.create_cycle.call_args
    sessions = call_kwargs.kwargs["sessions"]
    assert len(sessions) == 12

    # Week 1 should be problem_landscape, Week 2 should be position_pitch
    assert sessions[0]["week_type"] == "problem_landscape"
    assert sessions[1]["week_type"] == "position_pitch"

    # Arc mapping: weeks 1-2 = arc 1, weeks 3-4 = arc 2, etc.
    assert sessions[0]["arc_number"] == 1
    assert sessions[2]["arc_number"] == 2
    assert sessions[11]["arc_number"] == 6


async def test_create_cycle_rejects_number_below_one(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Cycle number must be at least 1."""
    data = CycleCreate(number=0, start_date="2026-04-10")
    with pytest.raises(ValidationError, match="at least 1"):
        await service.create_cycle(data)


async def test_create_cycle_computes_end_date(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """End date is start + 11 weeks."""
    mock_repo.create_cycle = AsyncMock(return_value=_CYCLE_ROW)
    data = CycleCreate(number=1, start_date="2026-04-10")
    await service.create_cycle(data)

    call_kwargs = mock_repo.create_cycle.call_args
    assert call_kwargs.kwargs["end_date"] == "2026-06-26"


async def test_get_current_cycle_raises_not_found(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Raises NotFoundError when no active cycle exists."""
    mock_repo.get_current_cycle = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError, match="No active cycle"):
        await service.get_current_cycle()


async def test_get_cycle_schedule_returns_schedule(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Returns a CycleScheduleResponse with cycle and sessions."""
    mock_repo.get_cycle_schedule = AsyncMock(
        return_value=(_CYCLE_ROW, [_SESSION_ROW])
    )

    result = await service.get_cycle_schedule("cycle-1")

    assert isinstance(result, CycleScheduleResponse)
    assert result.cycle.id == "cycle-1"
    assert len(result.sessions) == 1
    assert result.sessions[0].week_type == "problem_landscape"


async def test_get_cycle_schedule_raises_not_found(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Raises NotFoundError when cycle does not exist."""
    mock_repo.get_cycle_schedule = AsyncMock(return_value=(None, []))
    with pytest.raises(NotFoundError, match="not found"):
        await service.get_cycle_schedule("nonexistent")


async def test_update_session_assignment_raises_not_found(
    service: CycleService, mock_repo: MagicMock
) -> None:
    """Raises NotFoundError when session does not exist."""
    mock_repo.update_session_assignment = AsyncMock(return_value=None)
    with pytest.raises(NotFoundError, match="not found"):
        await service.update_session_assignment("ss-x", "a@b.com", None)
