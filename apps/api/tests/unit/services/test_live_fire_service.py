from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import NotFoundError, ValidationError
from models.live_fire import LiveFireCreate, LiveFireMetricsResponse, LiveFireResponse
from repositories.live_fire_repository import LiveFireRepository
from services.live_fire_service import LiveFireService


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock(spec=LiveFireRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> LiveFireService:
    return LiveFireService(mock_repo)


_ENTRY_ROW = {
    "id": "lf-1",
    "outcome": "used_successfully",
    "context": "Client meeting went well",
    "date": "2026-04-10",
    "position_id": "pos-1",
    "position_text": "Our agentic AI position",
    "reporter_name": "Dom",
    "reporter_email": "dom@valliance.com",
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}


async def test_create_entry_succeeds(
    service: LiveFireService, mock_repo: MagicMock
) -> None:
    """Creating a valid Live Fire entry succeeds."""
    mock_repo.create_entry = AsyncMock(return_value=_ENTRY_ROW)

    data = LiveFireCreate(
        outcome="used_successfully",
        context="Client meeting went well",
        date="2026-04-10",
        position_id="pos-1",
        reporter_email="dom@valliance.com",
    )
    result = await service.create_entry(data)
    assert isinstance(result, LiveFireResponse)
    assert result.outcome == "used_successfully"


async def test_create_entry_rejects_invalid_outcome(
    service: LiveFireService, mock_repo: MagicMock
) -> None:
    """Invalid outcome value raises ValidationError."""
    data = LiveFireCreate(
        outcome="invalid_outcome",
        context="Test",
        date="2026-04-10",
        position_id="pos-1",
        reporter_email="dom@valliance.com",
    )
    with pytest.raises(ValidationError, match="outcome"):
        await service.create_entry(data)


async def test_create_entry_raises_not_found_when_position_missing(
    service: LiveFireService, mock_repo: MagicMock
) -> None:
    """Raises NotFoundError when position or reporter not found."""
    mock_repo.create_entry = AsyncMock(return_value=None)

    data = LiveFireCreate(
        outcome="used_successfully",
        context="Test",
        date="2026-04-10",
        position_id="pos-nonexistent",
        reporter_email="nobody@valliance.com",
    )
    with pytest.raises(NotFoundError, match="not found"):
        await service.create_entry(data)


async def test_get_metrics_returns_response(
    service: LiveFireService, mock_repo: MagicMock
) -> None:
    """Metrics endpoint returns structured response."""
    mock_repo.get_metrics = AsyncMock(return_value=[
        {
            "position_id": "pos-1",
            "position_text": "Our position",
            "total_uses": 5,
            "successes": 3,
            "failures": 2,
            "success_rate": 0.6,
            "last_used": "2026-04-10",
            "never_used": False,
        },
        {
            "position_id": "pos-2",
            "position_text": "Another position",
            "total_uses": 0,
            "successes": 0,
            "failures": 0,
            "success_rate": None,
            "last_used": None,
            "never_used": True,
        },
    ])

    result = await service.get_metrics()
    assert isinstance(result, LiveFireMetricsResponse)
    assert len(result.metrics) == 2
    assert result.metrics[0].success_rate == 0.6
    assert result.metrics[1].never_used is True
