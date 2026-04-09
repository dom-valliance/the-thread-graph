from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class ArgumentRepository(BaseRepository):
    async def list_arguments(
        self,
        session_id: str | None = None,
        position_id: str | None = None,
        sentiment: str | None = None,
    ) -> list[dict[str, object]]:
        """List arguments with optional filtering by session, position, and sentiment."""
        where_clauses: list[str] = []
        params: dict[str, object] = {}

        if session_id is not None:
            where_clauses.append("s.id = $session_id")
            params["session_id"] = session_id

        if position_id is not None:
            where_clauses.append("p.id = $position_id")
            params["position_id"] = position_id

        if sentiment is not None:
            where_clauses.append("arg.sentiment = $sentiment")
            params["sentiment"] = sentiment

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Build optional matches based on filters to keep the query efficient
        position_match = (
            "MATCH (arg)-[:SUPPORTS|CHALLENGES]->(p:Position)"
            if position_id is not None
            else "OPTIONAL MATCH (arg)-[:SUPPORTS|CHALLENGES]->(p:Position)"
        )
        session_match = (
            "MATCH (arg)-[:MADE_IN]->(s:Session)"
            if session_id is not None
            else "OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)"
        )

        query = f"""
            MATCH (arg:Argument)
            {session_match}
            {position_match}
            {where}
            RETURN arg {{
                .id, .text, .sentiment, .strength, .speaker,
                .created_at, .updated_at,
                session_id: s.id
            }} AS argument
            ORDER BY arg.created_at DESC
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["argument"])) for record in records]

    async def get_argument(self, argument_id: str) -> dict[str, object] | None:
        """Get a single argument with its session and position relationships."""
        query = """
            MATCH (arg:Argument {id: $id})
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                .created_at, .updated_at,
                session_id: s.id
            } AS argument
        """
        records = await self._read(query, {"id": argument_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["argument"]))

    async def batch_create_arguments(
        self, arguments: list[dict[str, object]]
    ) -> int:
        """Create or update arguments in bulk using MERGE for idempotence.

        Returns the number of nodes created.
        """
        query = """
            UNWIND $arguments AS arg
            MERGE (a:Argument {id: arg.id})
            ON CREATE SET
                a.text = arg.text,
                a.sentiment = arg.sentiment,
                a.strength = arg.strength,
                a.speaker = arg.speaker,
                a.created_at = datetime(),
                a.updated_at = datetime()
            ON MATCH SET
                a.text = arg.text,
                a.sentiment = arg.sentiment,
                a.strength = arg.strength,
                a.speaker = arg.speaker,
                a.updated_at = datetime()
            WITH a, arg
            FOREACH (_ IN CASE WHEN arg.session_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (s:Session {id: arg.session_id})
                MERGE (a)-[:MADE_IN]->(s)
            )
            FOREACH (_ IN CASE WHEN arg.position_id IS NOT NULL AND arg.sentiment = 'supporting' THEN [1] ELSE [] END |
                MERGE (p:Position {id: arg.position_id})
                MERGE (a)-[:SUPPORTS]->(p)
            )
            FOREACH (_ IN CASE WHEN arg.position_id IS NOT NULL AND arg.sentiment = 'challenging' THEN [1] ELSE [] END |
                MERGE (p:Position {id: arg.position_id})
                MERGE (a)-[:CHALLENGES]->(p)
            )
        """
        summary = await self._write(query, {"arguments": arguments})
        return summary.counters.nodes_created
