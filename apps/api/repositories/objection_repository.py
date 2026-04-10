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

    async def list_objection_pairs_with_context(
        self, arc_name: str | None = None
    ) -> list[dict[str, object]]:
        """List objection-response pairs with position text and arc context."""
        where = "WHERE a.name = $arc_name" if arc_name else ""
        params: dict[str, object] = {}
        if arc_name:
            params["arc_name"] = arc_name

        query = f"""
            MATCH (orp:ObjectionResponsePair)-[:TESTED_BY]->(p:Position)
                  -[:LOCKED_IN]->(a:Arc)
            {where}
            RETURN orp {{
                .id, .objection_text, .response_text, .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                arc_name: a.name,
                arc_number: a.number
            }} AS pair
            ORDER BY a.number, orp.created_at DESC
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["pair"])) for record in records]

    async def create_objection_pair(
        self, data: dict[str, object]
    ) -> dict[str, object] | None:
        """Create a new objection-response pair linked to a position."""
        query = """
            MATCH (p:Position {id: $position_id})
            CREATE (orp:ObjectionResponsePair {
                id: $id,
                objection_text: $objection_text,
                response_text: $response_text,
                created_at: datetime(),
                updated_at: datetime()
            })
            CREATE (orp)-[:TESTED_BY]->(p)
            RETURN orp {
                .id, .objection_text, .response_text,
                .created_at, .updated_at,
                position_id: p.id
            } AS pair
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["pair"]))

    async def update_objection_pair(
        self, pair_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        """Update objection and response text for an existing pair."""
        query = """
            MATCH (orp:ObjectionResponsePair {id: $id})
            SET orp.objection_text = $objection_text,
                orp.response_text = $response_text,
                orp.updated_at = datetime()
            WITH orp
            OPTIONAL MATCH (orp)-[:TESTED_BY]->(p:Position)
            RETURN orp {
                .id, .objection_text, .response_text,
                .created_at, .updated_at,
                position_id: p.id
            } AS pair
        """
        records = await self._write_and_return(
            query, {"id": pair_id, **data}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["pair"]))

    async def delete_objection_pair(self, pair_id: str) -> bool:
        """Delete an objection-response pair and its relationships."""
        query = """
            MATCH (orp:ObjectionResponsePair {id: $id})
            DETACH DELETE orp
        """
        summary = await self._write(query, {"id": pair_id})
        return summary.counters.nodes_deleted > 0
