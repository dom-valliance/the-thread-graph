from __future__ import annotations

from uuid import uuid4

from core.exceptions import NotFoundError, ValidationError
from models.flash import FlashCreate, FlashResponse, FlashUpdate
from repositories.flash_repository import FlashRepository

VALID_STATUSES = {
    "pending", "reviewed_holds", "minor_update", "major_rewrite_scheduled"
}


class FlashService:
    def __init__(self, repository: FlashRepository) -> None:
        self._repo = repository

    async def create_flash(self, data: FlashCreate) -> FlashResponse:
        flash_id = str(uuid4())
        row = await self._repo.create_flash({
            "id": flash_id,
            "title": data.title,
            "description": data.description,
            "position_id": data.position_id,
            "raised_by_email": data.raised_by_email,
        })
        if row is None:
            raise NotFoundError("Position or person not found")
        return FlashResponse(**row)

    async def list_flashes(
        self,
        status: str | None = None,
        position_id: str | None = None,
    ) -> list[FlashResponse]:
        rows = await self._repo.list_flashes(
            status=status, position_id=position_id
        )
        return [FlashResponse(**row) for row in rows]

    async def get_pending(self) -> list[FlashResponse]:
        rows = await self._repo.get_pending()
        return [FlashResponse(**row) for row in rows]

    async def update_flash(
        self, flash_id: str, data: FlashUpdate
    ) -> FlashResponse:
        if data.status is not None and data.status not in VALID_STATUSES:
            raise ValidationError(
                f"status must be one of: {', '.join(sorted(VALID_STATUSES))}"
            )
        update_data = data.model_dump(exclude_none=True)
        row = await self._repo.update_flash(flash_id, update_data)
        if row is None:
            raise NotFoundError(f"Flash '{flash_id}' not found")
        return FlashResponse(**row)
