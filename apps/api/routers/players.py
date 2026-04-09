from __future__ import annotations

from fastapi import APIRouter, Depends
from neo4j import AsyncDriver

from core.dependencies import get_driver
from models.common import ApiResponse
from models.player import PlayerBookmarkResponse, PlayerResponse
from repositories.player_repository import PlayerRepository
from services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["players"])


def _get_service(driver: AsyncDriver = Depends(get_driver)) -> PlayerService:
    return PlayerService(PlayerRepository(driver))


@router.get("", response_model=ApiResponse[list[PlayerResponse]])
async def list_players(service: PlayerService = Depends(_get_service)) -> dict:
    """List all players with bookmark counts."""
    players = await service.list_players()
    return {"data": players, "meta": {"count": len(players)}}


@router.get(
    "/{name}/bookmarks",
    response_model=ApiResponse[list[PlayerBookmarkResponse]],
)
async def get_player_bookmarks(
    name: str,
    service: PlayerService = Depends(_get_service),
) -> dict:
    """Get bookmarks covering or published by a player."""
    bookmarks = await service.get_player_bookmarks(name)
    return {"data": bookmarks, "meta": {"count": len(bookmarks)}}
