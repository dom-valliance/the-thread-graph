from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.position import (
    ArgumentMapResponse,
    EvidenceTrailResponse,
    PositionCreate,
    PositionDetail,
    PositionLock,
    PositionResponse,
    PositionRevise,
    PositionUpdate,
    PositionVersionResponse,
)
from repositories.position_repository import PositionRepository
from services.position_service import PositionService

router = APIRouter(prefix="/positions", tags=["positions"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> PositionService:
    return PositionService(PositionRepository(driver))


@router.get("", response_model=ApiResponse[list[PositionResponse]])
async def list_positions(
    arc_number: int | None = Query(None),
    status: str | None = Query(None),
    proposition: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(25, ge=1, le=100),
    service: PositionService = Depends(_get_service),
) -> dict:
    """List positions with optional filtering by arc, status, and proposition."""
    positions = await service.list_positions(
        arc_number=arc_number,
        status=status,
        proposition=proposition,
        cursor=cursor,
        limit=limit,
    )
    return {
        "data": positions,
        "meta": {"count": len(positions), "cursor": positions[-1].id if positions else None, "has_more": len(positions) == limit},
    }


@router.post("", response_model=ApiResponse[PositionResponse], status_code=201)
async def create_position(
    body: PositionCreate,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Create a new position in draft status."""
    position = await service.create_position(body)
    return {"data": position}


@router.put("/{position_id}", response_model=ApiResponse[PositionResponse])
async def update_position(
    position_id: str,
    body: PositionUpdate,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Update a position. Only allowed when status is draft or under_revision."""
    position = await service.update_position(position_id, body)
    return {"data": position}


@router.post("/{position_id}/lock", response_model=ApiResponse[PositionResponse])
async def lock_position(
    position_id: str,
    body: PositionLock,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Lock a position. Validates required fields are present."""
    position = await service.lock_position(position_id, body)
    return {"data": position}


@router.post("/{position_id}/revise", response_model=ApiResponse[PositionResponse])
async def revise_position(
    position_id: str,
    body: PositionRevise,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Create a new version of a locked position for revision."""
    position = await service.revise_position(position_id, body)
    return {"data": position}


@router.get(
    "/{position_id}/versions",
    response_model=ApiResponse[list[PositionVersionResponse]],
)
async def get_position_versions(
    position_id: str,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Get version history for a position."""
    versions = await service.get_position_versions(position_id)
    return {"data": versions, "meta": {"count": len(versions)}}


@router.get("/{position_id}", response_model=ApiResponse[PositionDetail])
async def get_position(
    position_id: str,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Get position detail with anti-position, evidence chain, and arguments."""
    detail = await service.get_position_detail(position_id)
    return {"data": detail}


@router.get(
    "/{position_id}/arguments",
    response_model=ApiResponse[ArgumentMapResponse],
)
async def get_argument_map(
    position_id: str,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Get the full argument map for a position."""
    argument_map = await service.get_argument_map(position_id)
    return {"data": argument_map}


@router.get(
    "/{position_id}/evidence-trail",
    response_model=ApiResponse[EvidenceTrailResponse],
)
async def get_evidence_trail(
    position_id: str,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Get the evidence provenance trail for a position."""
    trail = await service.get_evidence_trail(position_id)
    return {"data": trail}


@router.get("/{position_id}/changes-since-lock", response_model=ApiResponse[dict])
async def get_changes_since_lock(
    position_id: str,
    service: PositionService = Depends(_get_service),
) -> dict:
    """Get evidence and arguments added after the position was locked."""
    changes = await service.get_changes_since_lock(position_id)
    return {"data": changes}
