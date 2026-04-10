from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.bridge import CrossArcBridgeResponse, UnconnectedPosition
from models.common import ApiResponse
from repositories.bridge_repository import BridgeRepository
from services.bridge_service import BridgeService

router = APIRouter(prefix="/bridges", tags=["bridges"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> BridgeService:
    return BridgeService(BridgeRepository(driver))


@router.get("", response_model=ApiResponse[list[CrossArcBridgeResponse]])
async def list_bridges(
    service: BridgeService = Depends(_get_service),
) -> dict:
    """Get all cross-arc position bridges."""
    bridges = await service.list_bridges()
    return {"data": bridges, "meta": {"count": len(bridges)}}


@router.get("/gaps", response_model=ApiResponse[list[UnconnectedPosition]])
async def list_gaps(
    service: BridgeService = Depends(_get_service),
) -> dict:
    """Get locked positions with no cross-arc bridges."""
    positions = await service.list_unconnected()
    return {"data": positions, "meta": {"count": len(positions)}}
