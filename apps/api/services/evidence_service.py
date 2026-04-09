from __future__ import annotations

from core.exceptions import NotFoundError
from models.evidence import EvidenceResponse
from repositories.evidence_repository import EvidenceRepository


class EvidenceService:
    def __init__(self, repository: EvidenceRepository) -> None:
        self._repo = repository

    async def list_evidence(
        self,
        position_id: str | None = None,
        type: str | None = None,
    ) -> list[EvidenceResponse]:
        rows = await self._repo.list_evidence(
            position_id=position_id,
            type=type,
        )
        return [EvidenceResponse(**row) for row in rows]

    async def get_evidence(self, evidence_id: str) -> EvidenceResponse:
        row = await self._repo.get_evidence(evidence_id)
        if row is None:
            raise NotFoundError(f"Evidence {evidence_id} not found")
        return EvidenceResponse(**row)

    async def batch_create_evidence(
        self, evidence_list: list[dict[str, object]]
    ) -> int:
        return await self._repo.batch_create_evidence(evidence_list)
