from __future__ import annotations

from core.exceptions import NotFoundError
from models.argument import ArgumentResponse
from repositories.argument_repository import ArgumentRepository


class ArgumentService:
    def __init__(self, repository: ArgumentRepository) -> None:
        self._repo = repository

    async def list_arguments(
        self,
        session_id: str | None = None,
        position_id: str | None = None,
        sentiment: str | None = None,
    ) -> list[ArgumentResponse]:
        rows = await self._repo.list_arguments(
            session_id=session_id,
            position_id=position_id,
            sentiment=sentiment,
        )
        return [ArgumentResponse(**row) for row in rows]

    async def get_argument(self, argument_id: str) -> ArgumentResponse:
        row = await self._repo.get_argument(argument_id)
        if row is None:
            raise NotFoundError(f"Argument {argument_id} not found")
        return ArgumentResponse(**row)

    async def batch_create_arguments(
        self, arguments: list[dict[str, object]]
    ) -> int:
        return await self._repo.batch_create_arguments(arguments)
