from __future__ import annotations

from core.exceptions import NotFoundError
from models.player import PlayerBookmarkResponse, PlayerResponse
from repositories.player_repository import PlayerRepository


class PlayerService:
    def __init__(self, repository: PlayerRepository) -> None:
        self._repo = repository

    async def list_players(self) -> list[PlayerResponse]:
        rows = await self._repo.list_players()
        return [PlayerResponse(**row) for row in rows]

    async def get_player_bookmarks(
        self, player_name: str
    ) -> list[PlayerBookmarkResponse]:
        rows = await self._repo.get_player_bookmarks(player_name)
        if not rows:
            # Verify the player exists before returning empty.
            players = await self._repo.list_players()
            names = [p["name"] for p in players]
            if player_name not in names:
                raise NotFoundError(f"Player '{player_name}' not found")
        return [PlayerBookmarkResponse(**row) for row in rows]
