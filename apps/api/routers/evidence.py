from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.evidence import EvidenceCreate, EvidenceResponse, EvidenceUpdate
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


@router.post("", response_model=ApiResponse[EvidenceResponse], status_code=201)
async def create_evidence(
    body: EvidenceCreate,
    service: EvidenceService = Depends(_get_service),
) -> dict:
    """Create a single evidence item linked to a position."""
    evidence = await service.create_evidence(body)
    return {"data": evidence}


@router.put("/{evidence_id}", response_model=ApiResponse[EvidenceResponse])
async def update_evidence(
    evidence_id: str,
    body: EvidenceUpdate,
    service: EvidenceService = Depends(_get_service),
) -> dict:
    """Update evidence text, type, and source bookmark."""
    evidence = await service.update_evidence(evidence_id, body)
    return {"data": evidence}


@router.delete("/{evidence_id}", status_code=204, response_model=None)
async def delete_evidence(
    evidence_id: str,
    service: EvidenceService = Depends(_get_service),
) -> None:
    """Delete an evidence item."""
    await service.delete_evidence(evidence_id)
