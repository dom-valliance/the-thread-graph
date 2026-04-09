from __future__ import annotations

from core.exceptions import NotFoundError
from models.objection import ObjectionResponsePairResponse
from repositories.objection_repository import ObjectionRepository


class ObjectionService:
    def __init__(self, repository: ObjectionRepository) -> None:
        self._repo = repository

    async def list_objection_pairs(
        self, position_id: str | None = None
    ) -> list[ObjectionResponsePairResponse]:
        rows = await self._repo.list_objection_pairs(position_id)
        return [ObjectionResponsePairResponse(**row) for row in rows]

    async def get_objection_pair(
        self, pair_id: str
    ) -> ObjectionResponsePairResponse:
        row = await self._repo.get_objection_pair(pair_id)
        if row is None:
            raise NotFoundError(f"Objection-response pair '{pair_id}' not found")
        return ObjectionResponsePairResponse(**row)
