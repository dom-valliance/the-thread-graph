from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import NotFoundError, ValidationError
from models.forge import ForgeCreate, ForgeResponse, ForgeUpdate
from repositories.forge_repository import ForgeRepository
from services.forge_service import ForgeService


@pytest.fixture()
def mock_repo() -> MagicMock:
    return MagicMock(spec=ForgeRepository)


@pytest.fixture()
def service(mock_repo: MagicMock) -> ForgeService:
    return ForgeService(mock_repo)


_ASSIGNMENT_ROW = {
    "id": "fa-1",
    "artefact_type": "briefing",
    "status": "assigned",
    "deadline": "2026-04-17",
    "storyboard_notes": None,
    "published_url": None,
    "editor_notes": None,
    "assigned_to_name": "Dom",
    "assigned_to_email": "dom@valliance.com",
    "editor_name": None,
    "editor_email": None,
    "session_id": "ss-c1-w1",
    "arc_name": "Agentic AI",
    "created_at": "2026-04-10T00:00:00Z",
    "updated_at": "2026-04-10T00:00:00Z",
}


# ---------------------------------------------------------------------------
# Status transition tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        ("assigned", "storyboarded"),
        ("storyboarded", "in_production"),
        ("in_production", "editor_review"),
        ("editor_review", "published"),
    ],
)
async def test_valid_status_transitions(
    service: ForgeService, mock_repo: MagicMock, current_status: str, new_status: str
) -> None:
    """Each valid status transition is accepted."""
    current = {**_ASSIGNMENT_ROW, "status": current_status}
    updated = {**_ASSIGNMENT_ROW, "status": new_status}
    mock_repo.get_assignment = AsyncMock(return_value=current)
    mock_repo.update_assignment = AsyncMock(return_value=updated)

    result = await service.update_assignment("fa-1", ForgeUpdate(status=new_status))
    assert result.status == new_status


@pytest.mark.parametrize(
    "current_status,new_status",
    [
        ("assigned", "published"),
        ("assigned", "in_production"),
        ("storyboarded", "published"),
        ("published", "assigned"),
    ],
)
async def test_invalid_status_transitions_rejected(
    service: ForgeService, mock_repo: MagicMock, current_status: str, new_status: str
) -> None:
    """Skipping statuses or going backwards raises ValidationError."""
    current = {**_ASSIGNMENT_ROW, "status": current_status}
    mock_repo.get_assignment = AsyncMock(return_value=current)

    with pytest.raises(ValidationError, match="Cannot transition"):
        await service.update_assignment("fa-1", ForgeUpdate(status=new_status))


async def test_update_nonexistent_assignment_raises_not_found(
    service: ForgeService, mock_repo: MagicMock
) -> None:
    """Updating a nonexistent assignment raises NotFoundError."""
    mock_repo.get_assignment = AsyncMock(return_value=None)
    mock_repo.update_assignment = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.update_assignment("fa-x", ForgeUpdate(storyboard_notes="notes"))
