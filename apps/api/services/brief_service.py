from __future__ import annotations

from uuid import uuid4

from core.exceptions import ConflictError, NotFoundError, ValidationError
from models.brief import (
    BriefCreate,
    BriefLock,
    BriefResponse,
    BriefUpdate,
    LandscapeGridEntryCreate,
    LandscapeGridEntryResponse,
    LandscapeGridResponse,
)
from repositories.brief_repository import BriefRepository


class BriefService:
    def __init__(self, repository: BriefRepository) -> None:
        self._repo = repository

    async def create_brief(self, data: BriefCreate) -> BriefResponse:
        brief_id = str(uuid4())
        row = await self._repo.create_brief({
            "id": brief_id,
            "problem_statement": data.problem_statement,
            "landscape_criteria": data.landscape_criteria,
            "steelman_summary": data.steelman_summary,
            "session_id": data.session_id,
            "arc_name": data.arc_name,
        })
        if row is None:
            raise NotFoundError("Failed to create brief")
        return BriefResponse(**row)

    async def get_brief(self, brief_id: str) -> BriefResponse:
        row = await self._repo.get_brief(brief_id)
        if row is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        grid_data = row.pop("landscape_grid", None)
        landscape_grid = None
        if grid_data is not None:
            landscape_grid = LandscapeGridResponse(
                id=grid_data["id"],
                entries=[LandscapeGridEntryResponse(**e) for e in grid_data.get("entries", [])],
            )
        return BriefResponse(**row, landscape_grid=landscape_grid)

    async def update_brief(self, brief_id: str, data: BriefUpdate) -> BriefResponse:
        status = await self._repo.get_brief_status(brief_id)
        if status is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        if status != "draft":
            raise ConflictError(f"Brief '{brief_id}' is locked and cannot be edited")

        update_data = data.model_dump(exclude_none=True)
        row = await self._repo.update_brief(brief_id, update_data)
        if row is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        return BriefResponse(**row)

    async def lock_brief(self, brief_id: str, data: BriefLock) -> BriefResponse:
        status = await self._repo.get_brief_status(brief_id)
        if status is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        if status == "locked":
            raise ConflictError(f"Brief '{brief_id}' is already locked")

        row = await self._repo.lock_brief(brief_id, data.locked_by)
        if row is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        return BriefResponse(**row)

    async def add_grid_entries(
        self, brief_id: str, entries: list[LandscapeGridEntryCreate]
    ) -> dict[str, object]:
        status = await self._repo.get_brief_status(brief_id)
        if status is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        if status == "locked":
            raise ConflictError(f"Brief '{brief_id}' is locked")

        if not entries:
            raise ValidationError("At least one grid entry is required")

        grid_id = str(uuid4())
        entry_dicts = [
            {
                "id": str(uuid4()),
                "player_name": e.player_name,
                "criterion": e.criterion,
                "rating": e.rating,
                "notes": e.notes,
            }
            for e in entries
        ]
        result = await self._repo.add_grid_entries(brief_id, grid_id, entry_dicts)
        if result is None:
            raise NotFoundError(f"Brief '{brief_id}' not found")
        return result
