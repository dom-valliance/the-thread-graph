from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.flash import FlashCreate, FlashResponse, FlashUpdate
from repositories.flash_repository import FlashRepository
from services.flash_service import FlashService

router = APIRouter(prefix="/flashes", tags=["flashes"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> FlashService:
    return FlashService(FlashRepository(driver))


@router.post("", response_model=ApiResponse[FlashResponse], status_code=201)
async def create_flash(
    body: FlashCreate,
    service: FlashService = Depends(_get_service),
) -> dict:
    """Submit a Flash."""
    flash = await service.create_flash(body)
    return {"data": flash}


@router.get("", response_model=ApiResponse[list[FlashResponse]])
async def list_flashes(
    status: str | None = Query(None),
    position_id: str | None = Query(None),
    service: FlashService = Depends(_get_service),
) -> dict:
    """List flashes with filters."""
    flashes = await service.list_flashes(status=status, position_id=position_id)
    return {"data": flashes, "meta": {"count": len(flashes)}}


@router.get("/pending", response_model=ApiResponse[list[FlashResponse]])
async def get_pending(
    service: FlashService = Depends(_get_service),
) -> dict:
    """Get pending flashes for the next Live Fire slot."""
    flashes = await service.get_pending()
    return {"data": flashes, "meta": {"count": len(flashes)}}


@router.put("/{flash_id}", response_model=ApiResponse[FlashResponse])
async def update_flash(
    flash_id: str,
    body: FlashUpdate,
    service: FlashService = Depends(_get_service),
) -> dict:
    """Update Flash status after review."""
    flash = await service.update_flash(flash_id, body)
    return {"data": flash}
