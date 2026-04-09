from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class SessionRepository(BaseRepository):
    async def list_sessions(
        self,
        arc: str | None = None,
        person: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List sessions with optional filters and cursor-based pagination."""
        conditions: list[str] = []
        params: dict[str, object] = {"limit": limit}

        if arc:
            conditions.append(
                "EXISTS { MATCH (s)-[:HAS_THEME]->(th:Theme {name: $arc}) }"
            )
            params["arc"] = arc

        if person:
            conditions.append(
                "EXISTS { MATCH (pe:Person {name: $person})-[:PRESENTED_IN]->(s) }"
            )
            params["person"] = person

        if date_from:
            conditions.append("s.date >= $date_from")
            params["date_from"] = date_from

        if date_to:
            conditions.append("s.date <= $date_to")
            params["date_to"] = date_to

        if cursor:
            conditions.append("s.notion_id > $cursor")
            params["cursor"] = cursor

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            MATCH (s:Session)
            {where_clause}
            OPTIONAL MATCH (s)-[:HAS_THEME]->(th:Theme)
            WITH s, th
            RETURN s {{
                .notion_id, .title, .date, .duration, .summary,
                .enrichment_status, .created_at, .updated_at,
                theme_name: th.name
            }} AS session
            ORDER BY session.date DESC, session.notion_id
            LIMIT $limit
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["session"])) for record in records]

    async def get_session(self, notion_id: str) -> dict[str, object] | None:
        """Get a single session by notion_id with related entities."""
        query = """
            MATCH (s:Session {notion_id: $notion_id})
            OPTIONAL MATCH (s)-[:HAS_THEME]->(th:Theme)
            WITH s, th
            OPTIONAL MATCH (s)-[:CONTAINED]->(arg:Argument)
            WITH s, th, collect(DISTINCT {id: arg.id, text: arg.text, sentiment: arg.sentiment}) AS arguments
            OPTIONAL MATCH (s)-[:GENERATED]->(ai:ActionItem)
            WITH s, th, arguments, collect(DISTINCT {id: ai.id, text: ai.text, status: ai.status}) AS action_items
            OPTIONAL MATCH (s)-[:REFERENCED]->(b:Bookmark)
            WITH s, th, arguments, action_items, collect(DISTINCT {notion_id: b.notion_id, title: b.title}) AS referenced_bookmarks
            RETURN s {
                .notion_id, .title, .date, .duration, .summary,
                .enrichment_status, .created_at, .updated_at,
                theme_name: th.name,
                arguments: arguments,
                action_items: action_items,
                referenced_bookmarks: referenced_bookmarks
            } AS session
        """
        records = await self._read(query, {"notion_id": notion_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["session"]))

    async def upsert_sessions(self, sessions: list[dict[str, object]]) -> int:
        """Upsert sessions via MERGE on notion_id. Returns count of rows processed."""
        query = """
            UNWIND $sessions AS sess
            MERGE (s:Session {notion_id: sess.notion_id})
                ON CREATE SET
                    s.title = sess.title,
                    s.date = sess.date,
                    s.duration = sess.duration,
                    s.summary = sess.summary,
                    s.enrichment_status = 'pending',
                    s.created_at = datetime(),
                    s.updated_at = datetime()
                ON MATCH SET
                    s.title = sess.title,
                    s.date = sess.date,
                    s.duration = sess.duration,
                    s.summary = sess.summary,
                    s.updated_at = datetime()
        """
        summary = await self._write(query, {"sessions": sessions})
        return summary.counters.nodes_created + summary.counters.properties_set
