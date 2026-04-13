from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import ConflictError, NotFoundError, ValidationError
from models.brief import BriefCreate, BriefLock, BriefUpdate, LandscapeGridEntryCreate
from repositories.brief_repository import BriefRepository
from services.brief_service import BriefService


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock(spec=BriefRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> BriefService:
    return BriefService(mock_repo)


_BRIEF_ROW = {
    "id": "brief-1",
    "problem_statement": "Why do enterprises fail?",
    "landscape_criteria": ["speed", "cost"],
    "steelman_summary": "Palantir is faster.",
    "status": "draft",
    "locked_date": None,
    "locked_by": None,
    "session_id": "ss-c1-w1",
    "arc_name": "Agentic AI",
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}


async def test_lock_brief_succeeds(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Locking a draft brief succeeds."""
    mock_repo.get_brief_status = AsyncMock(return_value="draft")
    locked = {**_BRIEF_ROW, "status": "locked", "locked_by": "dom@valliance.com"}
    mock_repo.lock_brief = AsyncMock(return_value=locked)

    result = await service.lock_brief("brief-1", BriefLock(locked_by="dom@valliance.com"))
    assert result.status == "locked"


async def test_lock_brief_rejects_already_locked(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Locking an already-locked brief raises ConflictError."""
    mock_repo.get_brief_status = AsyncMock(return_value="locked")

    with pytest.raises(ConflictError, match="already locked"):
        await service.lock_brief("brief-1", BriefLock(locked_by="dom@valliance.com"))


async def test_update_brief_rejects_locked(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Updating a locked brief raises ConflictError."""
    mock_repo.get_brief_status = AsyncMock(return_value="locked")

    with pytest.raises(ConflictError, match="locked"):
        await service.update_brief("brief-1", BriefUpdate(problem_statement="new"))


async def test_update_brief_succeeds_for_draft(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Updating a draft brief succeeds."""
    mock_repo.get_brief_status = AsyncMock(return_value="draft")
    updated = {**_BRIEF_ROW, "problem_statement": "Updated question"}
    mock_repo.update_brief = AsyncMock(return_value=updated)

    result = await service.update_brief("brief-1", BriefUpdate(problem_statement="Updated question"))
    assert result.problem_statement == "Updated question"


async def test_lock_brief_raises_not_found(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Locking a nonexistent brief raises NotFoundError."""
    mock_repo.get_brief_status = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.lock_brief("brief-x", BriefLock(locked_by="dom@valliance.com"))


async def test_add_grid_entries_rejects_locked(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """Adding grid entries to a locked brief raises ConflictError."""
    mock_repo.get_brief_status = AsyncMock(return_value="locked")

    with pytest.raises(ConflictError):
        await service.add_grid_entries("brief-1", [
            LandscapeGridEntryCreate(player_name="Palantir", criterion="Speed", rating="strong", notes="Fast")
        ])


async def test_add_grid_entries_rejects_empty_list(
    service: BriefService, mock_repo: MagicMock
) -> None:
    """At least one grid entry is required."""
    mock_repo.get_brief_status = AsyncMock(return_value="draft")

    with pytest.raises(ValidationError, match="At least one"):
        await service.add_grid_entries("brief-1", [])
