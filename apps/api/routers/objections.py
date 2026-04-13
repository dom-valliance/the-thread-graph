from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.objection import (
    ObjectionPairCreate,
    ObjectionPairUpdate,
    ObjectionPairWithContext,
    ObjectionResponsePairResponse,
)
from repositories.objection_repository import ObjectionRepository
from services.objection_service import ObjectionService

router = APIRouter(prefix="/objections", tags=["objections"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ObjectionService:
    return ObjectionService(ObjectionRepository(driver))


@router.get("", response_model=ApiResponse[list[ObjectionPairWithContext]])
async def list_objections(
    position_id: str | None = Query(default=None),
    arc_name: str | None = Query(default=None),
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """List objection-response pairs with position and arc context.

    Filterable by position_id or arc_name.
    """
    if position_id is not None:
        pairs = await service.list_objection_pairs(position_id)
    else:
        pairs = await service.list_with_context(arc_name)
    return {"data": pairs, "meta": {"count": len(pairs)}}


@router.post("", response_model=ApiResponse[ObjectionResponsePairResponse], status_code=201)
async def create_objection(
    body: ObjectionPairCreate,
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """Create a new objection-response pair linked to a position."""
    pair = await service.create_pair(body)
    return {"data": pair}


@router.get("/{pair_id}", response_model=ApiResponse[ObjectionResponsePairResponse])
async def get_objection(
    pair_id: str,
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """Get a single objection-response pair."""
    pair = await service.get_objection_pair(pair_id)
    return {"data": pair}


@router.put("/{pair_id}", response_model=ApiResponse[ObjectionResponsePairResponse])
async def update_objection(
    pair_id: str,
    body: ObjectionPairUpdate,
    service: ObjectionService = Depends(_get_service),
) -> dict:
    """Update objection and response text."""
    pair = await service.update_pair(pair_id, body)
    return {"data": pair}


@router.delete("/{pair_id}", status_code=204, response_model=None)
async def delete_objection(
    pair_id: str,
    service: ObjectionService = Depends(_get_service),
) -> None:
    """Delete an objection-response pair."""
    await service.delete_pair(pair_id)
