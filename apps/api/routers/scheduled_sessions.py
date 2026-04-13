from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.cycle import ScheduledSessionResponse
from repositories.cycle_repository import CycleRepository
from services.cycle_service import CycleService

router = APIRouter(prefix="/scheduled-sessions", tags=["scheduled-sessions"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> CycleService:
    return CycleService(CycleRepository(driver))


@router.get("/{session_id}", response_model=ApiResponse[ScheduledSessionResponse])
async def get_scheduled_session(
    session_id: str,
    service: CycleService = Depends(_get_service),
) -> dict:
    """Get a single scheduled session by ID."""
    session = await service.get_scheduled_session(session_id)
    return {"data": session}
