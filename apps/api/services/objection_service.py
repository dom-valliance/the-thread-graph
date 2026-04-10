from __future__ import annotations

from uuid import uuid4

from core.exceptions import NotFoundError
from models.objection import (
    ObjectionPairCreate,
    ObjectionPairUpdate,
    ObjectionPairWithContext,
    ObjectionResponsePairResponse,
)
from repositories.objection_repository import ObjectionRepository


class ObjectionService:
    def __init__(self, repository: ObjectionRepository) -> None:
        self._repo = repository

    async def list_objection_pairs(
        self, position_id: str | None = None
    ) -> list[ObjectionResponsePairResponse]:
        rows = await self._repo.list_objection_pairs(position_id)
        return [ObjectionResponsePairResponse(**row) for row in rows]

    async def list_with_context(
        self, arc_name: str | None = None
    ) -> list[ObjectionPairWithContext]:
        rows = await self._repo.list_objection_pairs_with_context(arc_name)
        return [ObjectionPairWithContext(**row) for row in rows]

    async def get_objection_pair(
        self, pair_id: str
    ) -> ObjectionResponsePairResponse:
        row = await self._repo.get_objection_pair(pair_id)
        if row is None:
            raise NotFoundError(f"Objection-response pair '{pair_id}' not found")
        return ObjectionResponsePairResponse(**row)

    async def create_pair(
        self, data: ObjectionPairCreate
    ) -> ObjectionResponsePairResponse:
        params = {
            "id": str(uuid4()),
            "objection_text": data.objection_text,
            "response_text": data.response_text,
            "position_id": data.position_id,
        }
        row = await self._repo.create_objection_pair(params)
        if row is None:
            raise NotFoundError(
                f"Position '{data.position_id}' not found"
            )
        return ObjectionResponsePairResponse(**row)

    async def update_pair(
        self, pair_id: str, data: ObjectionPairUpdate
    ) -> ObjectionResponsePairResponse:
        params = {
            "objection_text": data.objection_text,
            "response_text": data.response_text,
        }
        row = await self._repo.update_objection_pair(pair_id, params)
        if row is None:
            raise NotFoundError(
                f"Objection-response pair '{pair_id}' not found"
            )
        return ObjectionResponsePairResponse(**row)

    async def delete_pair(self, pair_id: str) -> None:
        deleted = await self._repo.delete_objection_pair(pair_id)
        if not deleted:
            raise NotFoundError(
                f"Objection-response pair '{pair_id}' not found"
            )
