from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.enrichment import (
    ActionItemCreate,
    ArgumentCreate,
    EnrichmentResult,
    EvidenceCreate,
)
from repositories.enrichment_repository import EnrichmentRepository
from services.enrichment_service import EnrichmentService

router = APIRouter(prefix="/enrichment", tags=["enrichment"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> EnrichmentService:
    return EnrichmentService(EnrichmentRepository(driver))


@router.post("/arguments", response_model=ApiResponse[EnrichmentResult])
async def create_arguments(
    arguments: list[ArgumentCreate],
    service: EnrichmentService = Depends(_get_service),
) -> dict:
    """Batch create or update arguments from the NLP pipeline."""
    result = await service.create_arguments(arguments)
    return {"data": result}


@router.post("/action-items", response_model=ApiResponse[EnrichmentResult])
async def create_action_items(
    items: list[ActionItemCreate],
    service: EnrichmentService = Depends(_get_service),
) -> dict:
    """Batch create or update action items from the NLP pipeline."""
    result = await service.create_action_items(items)
    return {"data": result}


@router.post("/evidence", response_model=ApiResponse[EnrichmentResult])
async def create_evidence(
    evidence: list[EvidenceCreate],
    service: EnrichmentService = Depends(_get_service),
) -> dict:
    """Batch create or update evidence from the NLP pipeline."""
    result = await service.create_evidence(evidence)
    return {"data": result}
