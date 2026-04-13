from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class SessionRepository(BaseRepository):
    async def list_sessions(
        self,
        arc: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List discussion recordings with optional filters and cursor pagination.

        Arc filter works via the linked bookmark's BELONGS_TO_ARC relationship.
        """
        conditions: list[str] = []
        params: dict[str, object] = {"limit": limit}

        if arc:
            conditions.append(
                "EXISTS { MATCH (b)-[:BELONGS_TO_ARC]->(a:Arc {name: $arc}) }"
            )
            params["arc"] = arc

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
            OPTIONAL MATCH (b:Bookmark)-[:DISCUSSED_IN]->(s)
            {where_clause}
            WITH s, b
            RETURN s {{
                .notion_id, .title, .date, .ai_suggested_viewpoint,
                .enrichment_status, .created_at, .updated_at,
                bookmark_notion_id: b.notion_id
            }} AS session
            ORDER BY session.date DESC, session.notion_id
            LIMIT $limit
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["session"])) for record in records]

    async def get_session(self, notion_id: str) -> dict[str, object] | None:
        """Get a single discussion recording with related entities."""
        query = """
            MATCH (s:Session {notion_id: $notion_id})
            OPTIONAL MATCH (b:Bookmark)-[:DISCUSSED_IN]->(s)
            WITH s, b
            OPTIONAL MATCH (s)-[:CONTAINED]->(arg:Argument)
            WITH s, b, collect(DISTINCT {id: arg.id, text: arg.text, sentiment: arg.sentiment}) AS arguments
            OPTIONAL MATCH (s)-[:GENERATED]->(ai:ActionItem)
            WITH s, b, arguments, collect(DISTINCT {id: ai.id, text: ai.text, status: ai.status}) AS action_items
            RETURN s {
                .notion_id, .title, .date, .ai_suggested_viewpoint,
                .enrichment_status, .created_at, .updated_at,
                bookmark_notion_id: b.notion_id,
                arguments: arguments,
                action_items: action_items
            } AS session
        """
        records = await self._read(query, {"notion_id": notion_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["session"]))
