from __future__ import annotations

from uuid import uuid4

from core.exceptions import NotFoundError, ValidationError
from models.forge import (
    ForgeCreate,
    ForgeResponse,
    ForgeTrackerResponse,
    ForgeUpdate,
)
from repositories.forge_repository import ForgeRepository

VALID_STATUSES = [
    "assigned", "storyboarded", "in_production", "editor_review", "published"
]

ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "assigned": ["storyboarded"],
    "storyboarded": ["in_production"],
    "in_production": ["editor_review"],
    "editor_review": ["published"],
    "published": [],
}


class ForgeService:
    def __init__(self, repository: ForgeRepository) -> None:
        self._repo = repository

    async def create_assignment(self, data: ForgeCreate) -> ForgeResponse:
        assignment_id = str(uuid4())
        row = await self._repo.create_assignment({
            "id": assignment_id,
            "artefact_type": data.artefact_type,
            "deadline": data.deadline,
            "assigned_to_email": data.assigned_to_email,
            "session_id": data.session_id,
            "arc_name": data.arc_name,
            "derived_from_id": data.derived_from_id,
            "storyboard_notes": data.storyboard_notes,
        })
        if row is None:
            raise NotFoundError("Assigned person not found")
        return ForgeResponse(**row)

    async def list_assignments(
        self,
        status: str | None = None,
        arc: str | None = None,
        person_email: str | None = None,
        cycle_id: str | None = None,
    ) -> list[ForgeResponse]:
        rows = await self._repo.list_assignments(
            status=status, arc=arc,
            person_email=person_email, cycle_id=cycle_id,
        )
        return [ForgeResponse(**row) for row in rows]

    async def get_assignment(self, assignment_id: str) -> ForgeResponse:
        row = await self._repo.get_assignment(assignment_id)
        if row is None:
            raise NotFoundError(f"Forge assignment '{assignment_id}' not found")
        return ForgeResponse(**row)

    async def update_assignment(
        self, assignment_id: str, data: ForgeUpdate
    ) -> ForgeResponse:
        if data.status is not None:
            current = await self._repo.get_assignment(assignment_id)
            if current is None:
                raise NotFoundError(
                    f"Forge assignment '{assignment_id}' not found"
                )
            current_status = current["status"]
            allowed = ALLOWED_TRANSITIONS.get(current_status, [])
            if data.status not in allowed:
                raise ValidationError(
                    f"Cannot transition from '{current_status}' to '{data.status}'. "
                    f"Allowed: {', '.join(allowed) or 'none'}"
                )

        update_data = data.model_dump(exclude_none=True)
        row = await self._repo.update_assignment(assignment_id, update_data)
        if row is None:
            raise NotFoundError(f"Forge assignment '{assignment_id}' not found")
        return ForgeResponse(**row)

    async def get_tracker(self, cycle_id: str) -> ForgeTrackerResponse:
        data = await self._repo.get_tracker(cycle_id)
        return ForgeTrackerResponse(**data)
