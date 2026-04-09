from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.objection import ObjectionResponsePairResponse
from repositories.objection_repository import ObjectionRepository
from services.objection_service import ObjectionService

router = APIRouter(prefix="/objections", tags=["objections"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ObjectionService:
    return ObjectionService(ObjectionRepository(driver))


@router.get("", response_model=ApiResponse[list[ObjectionResponsePairResponse]])
async def list_objections(
    position_id: str | None = Query(default=None),
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """List objection-response pairs, optionally filtered by position."""
    pairs = await service.list_objection_pairs(position_id)
    return {"data": pairs, "meta": {"count": len(pairs)}}


@router.get("/{pair_id}", response_model=ApiResponse[ObjectionResponsePairResponse])
async def get_objection(
    pair_id: str,
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """Get a single objection-response pair."""
    pair = await service.get_objection_pair(pair_id)
    return {"data": pair}
