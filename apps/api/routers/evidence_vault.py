from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.evidence import EvidenceResponse
from repositories.evidence_repository import EvidenceRepository
from services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence-vault", tags=["evidence-vault"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> EvidenceService:
    return EvidenceService(EvidenceRepository(driver))


@router.get("", response_model=ApiResponse[list[EvidenceResponse]])
async def list_vault_evidence(
    arc: str | None = Query(None),
    proposition: str | None = Query(None),
    vault_type: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    service: EvidenceService = Depends(_get_service),
) -> dict:
    """List evidence entries with vault-specific filters."""
    entries = await service.list_vault_evidence(
        arc=arc,
        proposition=proposition,
        vault_type=vault_type,
        date_from=date_from,
        date_to=date_to,
    )
    return {"data": entries, "meta": {"count": len(entries)}}
