from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.brief import (
    BriefCreate,
    BriefLock,
    BriefResponse,
    BriefUpdate,
    LandscapeGridEntryCreate,
)
from models.common import ApiResponse
from repositories.brief_repository import BriefRepository
from services.brief_service import BriefService

router = APIRouter(prefix="/briefs", tags=["briefs"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> BriefService:
    return BriefService(BriefRepository(driver))


@router.post("", response_model=ApiResponse[BriefResponse], status_code=201)
async def create_brief(
    body: BriefCreate,
    service: BriefService = Depends(_get_service),
) -> dict:
    """Create a Problem-Landscape Brief in draft status."""
    brief = await service.create_brief(body)
    return {"data": brief}


@router.get("/{brief_id}", response_model=ApiResponse[BriefResponse])
async def get_brief(
    brief_id: str,
    service: BriefService = Depends(_get_service),
) -> dict:
    """Get a brief with its landscape grid."""
    brief = await service.get_brief(brief_id)
    return {"data": brief}


@router.put("/{brief_id}", response_model=ApiResponse[BriefResponse])
async def update_brief(
    brief_id: str,
    body: BriefUpdate,
    service: BriefService = Depends(_get_service),
) -> dict:
    """Update a brief. Only allowed when status is draft."""
    brief = await service.update_brief(brief_id, body)
    return {"data": brief}


@router.post("/{brief_id}/lock", response_model=ApiResponse[BriefResponse])
async def lock_brief(
    brief_id: str,
    body: BriefLock,
    service: BriefService = Depends(_get_service),
) -> dict:
    """Lock a brief. Rejects if already locked."""
    brief = await service.lock_brief(brief_id, body)
    return {"data": brief}


@router.post("/{brief_id}/grid-entries", response_model=ApiResponse[dict])
async def add_grid_entries(
    brief_id: str,
    body: list[LandscapeGridEntryCreate],
    service: BriefService = Depends(_get_service),
) -> dict:
    """Add landscape grid entries to a brief."""
    result = await service.add_grid_entries(brief_id, body)
    return {"data": result}
