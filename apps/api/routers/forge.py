from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.forge import (
    ForgeCreate,
    ForgeResponse,
    ForgeTrackerResponse,
    ForgeUpdate,
)
from repositories.forge_repository import ForgeRepository
from services.forge_service import ForgeService

router = APIRouter(prefix="/forge", tags=["forge"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ForgeService:
    return ForgeService(ForgeRepository(driver))


@router.get("/tracker", response_model=ApiResponse[ForgeTrackerResponse])
async def get_tracker(
    cycle_id: str = Query(...),
    service: ForgeService = Depends(_get_service),
) -> dict:
    """Get cycle-level artefact tracker."""
    tracker = await service.get_tracker(cycle_id)
    return {"data": tracker}


@router.post("", response_model=ApiResponse[ForgeResponse], status_code=201)
async def create_assignment(
    body: ForgeCreate,
    service: ForgeService = Depends(_get_service),
) -> dict:
    """Create a Forge assignment."""
    assignment = await service.create_assignment(body)
    return {"data": assignment}


@router.get("", response_model=ApiResponse[list[ForgeResponse]])
async def list_assignments(
    status: str | None = Query(None),
    arc: str | None = Query(None),
    person: str | None = Query(None),
    cycle_id: str | None = Query(None),
    service: ForgeService = Depends(_get_service),
) -> dict:
    """List Forge assignments with filters."""
    assignments = await service.list_assignments(
        status=status, arc=arc,
        person_email=person, cycle_id=cycle_id,
    )
    return {"data": assignments, "meta": {"count": len(assignments)}}


@router.get("/{assignment_id}", response_model=ApiResponse[ForgeResponse])
async def get_assignment(
    assignment_id: str,
    service: ForgeService = Depends(_get_service),
) -> dict:
    """Get a single Forge assignment."""
    assignment = await service.get_assignment(assignment_id)
    return {"data": assignment}


@router.put("/{assignment_id}", response_model=ApiResponse[ForgeResponse])
async def update_assignment(
    assignment_id: str,
    body: ForgeUpdate,
    service: ForgeService = Depends(_get_service),
) -> dict:
    """Update a Forge assignment. Status transitions are validated."""
    assignment = await service.update_assignment(assignment_id, body)
    return {"data": assignment}
