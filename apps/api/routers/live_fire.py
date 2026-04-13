from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.live_fire import (
    LiveFireCreate,
    LiveFireMetricsResponse,
    LiveFireResponse,
)
from repositories.live_fire_repository import LiveFireRepository
from services.live_fire_service import LiveFireService

router = APIRouter(prefix="/live-fire", tags=["live-fire"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> LiveFireService:
    return LiveFireService(LiveFireRepository(driver))


@router.post("", response_model=ApiResponse[LiveFireResponse], status_code=201)
async def create_entry(
    body: LiveFireCreate,
    service: LiveFireService = Depends(_get_service),
) -> dict:
    """Submit a Live Fire entry."""
    entry = await service.create_entry(body)
    return {"data": entry}


@router.get("", response_model=ApiResponse[list[LiveFireResponse]])
async def list_entries(
    position_id: str | None = Query(None),
    outcome: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    service: LiveFireService = Depends(_get_service),
) -> dict:
    """List Live Fire entries with filters."""
    entries = await service.list_entries(
        position_id=position_id,
        outcome=outcome,
        date_from=date_from,
        date_to=date_to,
    )
    return {"data": entries, "meta": {"count": len(entries)}}


@router.get("/metrics", response_model=ApiResponse[LiveFireMetricsResponse])
async def get_metrics(
    service: LiveFireService = Depends(_get_service),
) -> dict:
    """Get aggregated Live Fire metrics per position."""
    metrics = await service.get_metrics()
    return {"data": metrics}
