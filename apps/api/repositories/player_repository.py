from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class PlayerRepository(BaseRepository):
    async def list_players(self) -> list[dict[str, object]]:
        """List all players with a count of bookmarks they appear in."""
        query = """
            MATCH (pl:Player)
            OPTIONAL MATCH (b:Bookmark)-[:COVERS_PLAYER|PUBLISHED_BY]->(pl)
            WITH pl, count(DISTINCT b) AS bookmark_count
            RETURN pl {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count
            } AS player
            ORDER BY player.name
        """
        records = await self._read(query)
        return [serialise_record(dict(record["player"])) for record in records]

    async def get_player_bookmarks(
        self, player_name: str
    ) -> list[dict[str, object]]:
        """Get bookmarks that cover or are published by a given player."""
        query = """
            MATCH (b:Bookmark)-[:COVERS_PLAYER|PUBLISHED_BY]->(pl:Player {name: $name})
            RETURN b {
                .id, .title, .source, .url, .ai_summary, .created_at, .updated_at
            } AS bookmark
            ORDER BY b.created_at DESC
        """
        records = await self._read(query, {"name": player_name})
        return [serialise_record(dict(record["bookmark"])) for record in records]
