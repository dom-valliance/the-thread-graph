from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.arc import ArcDetail, ArcResponse, ThemeBridgeResponse
from models.common import ApiResponse
from repositories.arc_repository import ArcRepository
from services.arc_service import ArcService

router = APIRouter(prefix="/arcs", tags=["arcs"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ArcService:
    return ArcService(ArcRepository(driver))


@router.get("", response_model=ApiResponse[list[ArcResponse]])
async def list_arcs(service: ArcService = Depends(_get_service)) -> dict:
    """List all themes (arcs) with bookmark and session counts."""
    arcs = await service.list_arcs()
    return {"data": arcs, "meta": {"count": len(arcs)}}


@router.get("/bridges", response_model=ApiResponse[list[ThemeBridgeResponse]])
async def get_bridges(service: ArcService = Depends(_get_service)) -> dict:
    """Get theme co-occurrence edges."""
    bridges = await service.get_bridges()
    return {"data": bridges, "meta": {"count": len(bridges)}}


@router.get("/{arc_name}", response_model=ApiResponse[ArcDetail])
async def get_arc(
    arc_name: str,
    service: ArcService = Depends(_get_service),
) -> dict:
    """Get theme detail with associated bookmarks."""
    detail = await service.get_arc_detail(arc_name)
    return {"data": detail}
