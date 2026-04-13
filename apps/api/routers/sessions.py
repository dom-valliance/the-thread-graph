from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.session import SessionDetail, SessionResponse
from repositories.session_repository import SessionRepository
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> SessionService:
    return SessionService(SessionRepository(driver))


@router.get("", response_model=ApiResponse[list[SessionResponse]])
async def list_sessions(
    arc: str | None = Query(None, description="Filter by arc name"),
    date_from: str | None = Query(None, description="Filter from this date"),
    date_to: str | None = Query(None, description="Filter up to this date"),
    cursor: str | None = Query(None, description="Cursor for pagination"),
    limit: int = Query(25, ge=1, le=100, description="Page size"),
    service: SessionService = Depends(_get_service),
) -> dict:
    """List discussion recordings with optional filters."""
    sessions = await service.list_sessions(
        arc=arc,
        date_from=date_from,
        date_to=date_to,
        cursor=cursor,
        limit=limit,
    )
    return {"data": sessions, "meta": {"count": len(sessions)}}


@router.get("/{notion_id}", response_model=ApiResponse[SessionDetail])
async def get_session(
    notion_id: str,
    service: SessionService = Depends(_get_service),
) -> dict:
    """Get a single discussion recording with arguments and action items."""
    detail = await service.get_session_detail(notion_id)
    return {"data": detail}
