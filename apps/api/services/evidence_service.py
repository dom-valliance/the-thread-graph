from __future__ import annotations

from uuid import uuid4

from core.exceptions import NotFoundError
from models.evidence import EvidenceCreate, EvidenceResponse, EvidenceUpdate
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

    async def create_evidence(
        self, data: EvidenceCreate
    ) -> EvidenceResponse:
        params = {
            "id": str(uuid4()),
            "text": data.text,
            "type": data.type,
            "position_id": data.position_id,
            "source_bookmark_id": data.source_bookmark_id,
        }
        row = await self._repo.create_evidence(params)
        if row is None:
            raise NotFoundError(
                f"Position '{data.position_id}' not found"
            )
        return EvidenceResponse(**row)

    async def update_evidence(
        self, evidence_id: str, data: EvidenceUpdate
    ) -> EvidenceResponse:
        params = {
            "text": data.text,
            "type": data.type,
            "source_bookmark_id": data.source_bookmark_id,
        }
        row = await self._repo.update_evidence(evidence_id, params)
        if row is None:
            raise NotFoundError(f"Evidence '{evidence_id}' not found")
        return EvidenceResponse(**row)

    async def delete_evidence(self, evidence_id: str) -> None:
        deleted = await self._repo.delete_evidence(evidence_id)
        if not deleted:
            raise NotFoundError(f"Evidence '{evidence_id}' not found")

    async def list_vault_evidence(
        self,
        arc: str | None = None,
        proposition: str | None = None,
        vault_type: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[EvidenceResponse]:
        rows = await self._repo.list_vault_evidence(
            arc=arc,
            proposition=proposition,
            vault_type=vault_type,
            date_from=date_from,
            date_to=date_to,
        )
        return [EvidenceResponse(**row) for row in rows]

    async def batch_create_evidence(
        self, evidence_list: list[dict[str, object]]
    ) -> int:
        return await self._repo.batch_create_evidence(evidence_list)
