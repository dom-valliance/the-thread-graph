from __future__ import annotations

from core.exceptions import NotFoundError
from models.position import (
    ArgumentMapResponse,
    ArgumentSummary,
    EvidenceChainItem,
    ObjectionPair,
    PositionDetail,
    PositionResponse,
    SteelmanItem,
)
from repositories.position_repository import PositionRepository


class PositionService:
    def __init__(self, repository: PositionRepository) -> None:
        self._repo = repository

    async def list_positions(
        self,
        arc_number: int | None = None,
        status: str | None = None,
        proposition: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[PositionResponse]:
        rows = await self._repo.list_positions(
            arc_number=arc_number,
            status=status,
            proposition=proposition,
            cursor=cursor,
            limit=limit,
        )
        return [PositionResponse(**row) for row in rows]

    async def get_position_detail(self, position_id: str) -> PositionDetail:
        row = await self._repo.get_position(position_id)
        if row is None:
            raise NotFoundError(f"Position {position_id} not found")
        return PositionDetail(
            **{k: v for k, v in row.items() if k not in (
                "anti_position", "evidence_chain",
                "supporting_arguments", "challenging_arguments",
            )},
            anti_position=row["anti_position"],
            evidence_chain=[
                EvidenceChainItem(**e) for e in row["evidence_chain"]
            ],
            supporting_arguments=[
                ArgumentSummary(**a) for a in row["supporting_arguments"]
            ],
            challenging_arguments=[
                ArgumentSummary(**a) for a in row["challenging_arguments"]
            ],
        )

    async def get_argument_map(self, position_id: str) -> ArgumentMapResponse:
        row = await self._repo.get_argument_map(position_id)
        if row is None:
            raise NotFoundError(f"Position {position_id} not found")
        return ArgumentMapResponse(
            position=PositionResponse(**row["position"]),
            supporting=[ArgumentSummary(**a) for a in row["supporting"]],
            challenging=[ArgumentSummary(**a) for a in row["challenging"]],
            steelman=[SteelmanItem(**s) for s in row["steelman"]],
            objection_pairs=[ObjectionPair(**o) for o in row["objection_pairs"]],
        )

    async def get_changes_since_lock(
        self, position_id: str
    ) -> dict[str, object]:
        result = await self._repo.get_changes_since_lock(position_id)
        if result is None:
            raise NotFoundError(f"Position {position_id} not found")
        return {
            "new_evidence": [
                EvidenceChainItem(**e) for e in result["new_evidence"]
            ],
            "new_arguments": [
                ArgumentSummary(**a) for a in result["new_arguments"]
            ],
        }
