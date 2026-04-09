from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.evidence import EvidenceResponse
from repositories.evidence_repository import EvidenceRepository
from services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["evidence"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> EvidenceService:
    return EvidenceService(EvidenceRepository(driver))


@router.get("", response_model=ApiResponse[list[EvidenceResponse]])
async def list_evidence(
    position_id: str | None = Query(None),
    type: str | None = Query(None),
    service: EvidenceService = Depends(_get_service),
) -> dict:
    """List evidence with optional filtering by position and type."""
    evidence = await service.list_evidence(
        position_id=position_id,
        type=type,
    )
    return {"data": evidence, "meta": {"count": len(evidence)}}
