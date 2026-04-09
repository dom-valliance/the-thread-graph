from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class ObjectionRepository(BaseRepository):
    async def list_objection_pairs(
        self, position_id: str | None = None
    ) -> list[dict[str, object]]:
        """List objection-response pairs, optionally filtered by position."""
        if position_id is not None:
            query = """
                MATCH (orp:ObjectionResponsePair)-[:TESTED_BY]->(p:Position {id: $position_id})
                RETURN orp {
                    .id, .objection_text, .response_text,
                    .created_at, .updated_at,
                    position_id: p.id
                } AS pair
                ORDER BY orp.created_at DESC
            """
            records = await self._read(query, {"position_id": position_id})
        else:
            query = """
                MATCH (orp:ObjectionResponsePair)
                OPTIONAL MATCH (orp)-[:TESTED_BY]->(p:Position)
                RETURN orp {
                    .id, .objection_text, .response_text,
                    .created_at, .updated_at,
                    position_id: p.id
                } AS pair
                ORDER BY orp.created_at DESC
            """
            records = await self._read(query)
        return [serialise_record(dict(record["pair"])) for record in records]

    async def get_objection_pair(
        self, pair_id: str
    ) -> dict[str, object] | None:
        """Get a single objection-response pair by ID."""
        query = """
            MATCH (orp:ObjectionResponsePair {id: $id})
            OPTIONAL MATCH (orp)-[:TESTED_BY]->(p:Position)
            RETURN orp {
                .id, .objection_text, .response_text,
                .created_at, .updated_at,
                position_id: p.id
            } AS pair
        """
        records = await self._read(query, {"id": pair_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["pair"]))
