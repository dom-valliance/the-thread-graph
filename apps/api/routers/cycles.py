from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.cycle import (
    CycleCreate,
    CycleCurrentResponse,
    CycleResponse,
    CycleScheduleResponse,
    LeadShadowAssignment,
    ScheduledSessionResponse,
)
from repositories.cycle_repository import CycleRepository
from services.cycle_service import CycleService

router = APIRouter(prefix="/cycles", tags=["cycles"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> CycleService:
    return CycleService(CycleRepository(driver))


@router.get("", response_model=ApiResponse[list[CycleResponse]])
async def list_cycles(service: CycleService = Depends(_get_service)) -> dict:
    """List all cycles."""
    cycles = await service.list_cycles()
    return {"data": cycles, "meta": {"count": len(cycles)}}


@router.get("/current", response_model=ApiResponse[CycleCurrentResponse])
async def get_current_cycle(
    service: CycleService = Depends(_get_service),
) -> dict:
    """Get the current active cycle with session info."""
    current = await service.get_current_cycle()
    return {"data": current}


@router.post("", response_model=ApiResponse[CycleResponse], status_code=201)
async def create_cycle(
    body: CycleCreate,
    service: CycleService = Depends(_get_service),
) -> dict:
    """Create a new cycle with 12 scheduled sessions."""
    cycle = await service.create_cycle(body)
    return {"data": cycle}


@router.get("/{cycle_id}/schedule", response_model=ApiResponse[CycleScheduleResponse])
async def get_cycle_schedule(
    cycle_id: str,
    service: CycleService = Depends(_get_service),
) -> dict:
    """Get the full 12-week schedule for a cycle."""
    schedule = await service.get_cycle_schedule(cycle_id)
    return {"data": schedule}


@router.put(
    "/{cycle_id}/schedule/{session_id}",
    response_model=ApiResponse[ScheduledSessionResponse],
)
async def update_session_assignment(
    cycle_id: str,
    session_id: str,
    body: LeadShadowAssignment,
    service: CycleService = Depends(_get_service),
) -> dict:
    """Update lead/shadow assignment for a scheduled session."""
    session = await service.update_session_assignment(
        session_id, body.lead_email, body.shadow_email
    )
    return {"data": session}
