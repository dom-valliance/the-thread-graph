from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.exceptions import ConflictError, NotFoundError, ValidationError
from models.position import PositionCreate, PositionLock, PositionRevise, PositionUpdate
from repositories.position_repository import PositionRepository
from services.position_service import PositionService


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock(spec=PositionRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> PositionService:
    return PositionService(mock_repo)


_DRAFT_POSITION = {
    "id": "pos-1",
    "text": "Our position on agentic AI",
    "status": "draft",
    "version": 1,
    "locked_date": None,
    "locked_by": None,
    "arc_number": 1,
    "proposition": None,
    "anti_position_text": "The counter argument",
    "cross_arc_bridge_text": "Links to Arc 2",
    "p1_v1_mapping": "P1",
    "steelman_addressed": None,
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}

_LOCKED_POSITION = {**_DRAFT_POSITION, "status": "locked", "locked_by": "test@valliance.com"}


# ---------------------------------------------------------------------------
# Lock tests
# ---------------------------------------------------------------------------


async def test_lock_position_succeeds_with_required_fields(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Locking a draft position with all required fields succeeds."""
    mock_repo.get_position_basic = AsyncMock(return_value=_DRAFT_POSITION)
    mock_repo.lock_position = AsyncMock(return_value=_LOCKED_POSITION)

    result = await service.lock_position("pos-1", PositionLock(locked_by="test@valliance.com"))

    assert result.status == "locked"
    mock_repo.lock_position.assert_awaited_once()


async def test_lock_position_rejects_already_locked(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Locking an already-locked position raises ConflictError."""
    mock_repo.get_position_basic = AsyncMock(return_value=_LOCKED_POSITION)

    with pytest.raises(ConflictError, match="already locked"):
        await service.lock_position("pos-1", PositionLock(locked_by="test@valliance.com"))


async def test_lock_position_rejects_missing_fields(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Locking fails with ValidationError listing missing required fields."""
    incomplete = {**_DRAFT_POSITION, "anti_position_text": None, "p1_v1_mapping": None}
    mock_repo.get_position_basic = AsyncMock(return_value=incomplete)

    with pytest.raises(ValidationError, match="anti_position_text") as exc_info:
        await service.lock_position("pos-1", PositionLock(locked_by="test@valliance.com"))
    assert "p1_v1_mapping" in str(exc_info.value)


async def test_lock_position_raises_not_found(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Locking a nonexistent position raises NotFoundError."""
    mock_repo.get_position_basic = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.lock_position("pos-x", PositionLock(locked_by="test@valliance.com"))


# ---------------------------------------------------------------------------
# Revise tests
# ---------------------------------------------------------------------------


async def test_revise_creates_new_version(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Revising a locked position creates a new draft version."""
    mock_repo.get_position_basic = AsyncMock(return_value=_LOCKED_POSITION)
    new_version = {**_DRAFT_POSITION, "id": "pos-2", "version": 2, "status": "draft"}
    mock_repo.revise_position = AsyncMock(return_value=new_version)

    result = await service.revise_position(
        "pos-1", PositionRevise(trigger_type="live_fire", trigger_id="lf-1")
    )

    assert result.version == 2
    assert result.status == "draft"
    mock_repo.revise_position.assert_awaited_once()


async def test_revise_rejects_draft_position(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Only locked positions can be revised."""
    mock_repo.get_position_basic = AsyncMock(return_value=_DRAFT_POSITION)

    with pytest.raises(ConflictError, match="Only locked"):
        await service.revise_position(
            "pos-1", PositionRevise(trigger_type="live_fire", trigger_id="lf-1")
        )


async def test_revise_rejects_invalid_trigger_type(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Trigger type must be live_fire or flash."""
    with pytest.raises(ValidationError, match="trigger_type"):
        await service.revise_position(
            "pos-1", PositionRevise(trigger_type="invalid", trigger_id="x")
        )


# ---------------------------------------------------------------------------
# Update tests
# ---------------------------------------------------------------------------


async def test_update_position_rejects_locked(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Updating a locked position raises ConflictError."""
    mock_repo.get_position_basic = AsyncMock(return_value=_LOCKED_POSITION)

    with pytest.raises(ConflictError, match="locked"):
        await service.update_position("pos-1", PositionUpdate(text="new text"))


async def test_update_position_succeeds_for_draft(
    service: PositionService, mock_repo: MagicMock
) -> None:
    """Updating a draft position succeeds."""
    mock_repo.get_position_basic = AsyncMock(return_value=_DRAFT_POSITION)
    updated = {**_DRAFT_POSITION, "text": "updated text"}
    mock_repo.update_position = AsyncMock(return_value=updated)

    result = await service.update_position("pos-1", PositionUpdate(text="updated text"))
    assert result.text == "updated text"
