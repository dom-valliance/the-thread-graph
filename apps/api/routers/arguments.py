from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.argument import ArgumentResponse
from models.common import ApiResponse
from repositories.argument_repository import ArgumentRepository
from services.argument_service import ArgumentService

router = APIRouter(prefix="/arguments", tags=["arguments"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> ArgumentService:
    return ArgumentService(ArgumentRepository(driver))


@router.get("", response_model=ApiResponse[list[ArgumentResponse]])
async def list_arguments(
    session_id: str | None = Query(None),
    position_id: str | None = Query(None),
    sentiment: str | None = Query(None),
    service: ArgumentService = Depends(_get_service),
) -> dict:
    """List arguments with optional filtering by session, position, and sentiment."""
    arguments = await service.list_arguments(
        session_id=session_id,
        position_id=position_id,
        sentiment=sentiment,
    )
    return {"data": arguments, "meta": {"count": len(arguments)}}
