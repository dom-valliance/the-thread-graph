from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class BookmarkRepository(BaseRepository):
    async def list_bookmarks(
        self,
        topic: str | None = None,
        theme: str | None = None,
        edge_or_foundational: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List bookmarks with optional filters and cursor-based pagination."""
        conditions: list[str] = []
        params: dict[str, object] = {"limit": limit}

        if topic:
            conditions.append(
                "EXISTS { MATCH (b)-[:TAGGED_WITH]->(:Topic {name: $topic}) }"
            )
            params["topic"] = topic

        if theme:
            conditions.append(
                "EXISTS { MATCH (b)-[:HAS_THEME]->(:Theme {name: $theme}) }"
            )
            params["theme"] = theme

        if edge_or_foundational:
            conditions.append("b.edge_or_foundational = $edge_or_foundational")
            params["edge_or_foundational"] = edge_or_foundational

        if cursor:
            conditions.append("b.notion_id > $cursor")
            params["cursor"] = cursor

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            MATCH (b:Bookmark)
            {where_clause}
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, collect(DISTINCT t.name) AS topic_names
            OPTIONAL MATCH (b)-[:HAS_THEME]->(th:Theme)
            WITH b, topic_names, th
            OPTIONAL MATCH (b)-[:EVIDENCES]->(:Position)-[:LOCKED_IN]->(a:Arc)
            WITH b, topic_names, th, collect(DISTINCT a.name) AS arc_names
            RETURN b {{
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .time_consumption, .date_added, .created_at, .updated_at,
                topic_names: topic_names,
                theme_name: th.name,
                arc_names: arc_names
            }} AS bookmark
            ORDER BY bookmark.notion_id
            LIMIT $limit
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def get_bookmark(self, notion_id: str) -> dict[str, object] | None:
        """Get a single bookmark by notion_id with all relationships."""
        query = """
            MATCH (b:Bookmark {notion_id: $notion_id})
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, collect(DISTINCT t.name) AS topic_names
            OPTIONAL MATCH (b)-[:HAS_THEME]->(th:Theme)
            WITH b, topic_names, th
            OPTIONAL MATCH (b)-[:EVIDENCES]->(p:Position)
            WITH b, topic_names, th, collect(DISTINCT {id: p.id, text: p.text}) AS related_positions
            OPTIONAL MATCH (s:Session)-[:REFERENCED]->(b)
            WITH b, topic_names, th, related_positions, collect(DISTINCT {notion_id: s.notion_id, title: s.title}) AS related_sessions
            RETURN b {
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .time_consumption, .date_added, .created_at, .updated_at,
                topic_names: topic_names,
                theme_name: th.name,
                related_positions: related_positions,
                related_sessions: related_sessions
            } AS bookmark
        """
        records = await self._read(query, {"notion_id": notion_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["bookmark"]))

    async def get_high_connectivity_bookmarks(self) -> list[dict[str, object]]:
        """Get bookmarks that evidence positions across multiple arcs."""
        query = """
            MATCH (b:Bookmark)-[:EVIDENCES]->(p:Position)-[:LOCKED_IN]->(a:Arc)
            WITH b, collect(DISTINCT a.number) AS arc_numbers, count(DISTINCT p) AS position_count
            WHERE size(arc_numbers) > 1
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, arc_numbers, position_count, collect(DISTINCT t.name) AS topic_names
            OPTIONAL MATCH (b)-[:HAS_THEME]->(th:Theme)
            RETURN b {
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .time_consumption, .date_added, .created_at, .updated_at,
                topic_names: topic_names,
                theme_name: th.name,
                position_count: position_count
            } AS bookmark
            ORDER BY bookmark.position_count DESC
        """
        records = await self._read(query)
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def upsert_bookmarks(self, bookmarks: list[dict[str, object]]) -> int:
        """Upsert bookmarks via MERGE on notion_id. Returns count of rows processed."""
        query = """
            UNWIND $bookmarks AS bk
            MERGE (b:Bookmark {notion_id: bk.notion_id})
                ON CREATE SET
                    b.title = bk.title,
                    b.source = bk.source,
                    b.url = bk.url,
                    b.ai_summary = bk.ai_summary,
                    b.valliance_viewpoint = bk.valliance_viewpoint,
                    b.edge_or_foundational = bk.edge_or_foundational,
                    b.focus = bk.focus,
                    b.time_consumption = bk.time_consumption,
                    b.date_added = bk.date_added,
                    b.created_at = datetime(),
                    b.updated_at = datetime()
                ON MATCH SET
                    b.title = bk.title,
                    b.source = bk.source,
                    b.url = bk.url,
                    b.ai_summary = bk.ai_summary,
                    b.valliance_viewpoint = bk.valliance_viewpoint,
                    b.edge_or_foundational = bk.edge_or_foundational,
                    b.focus = bk.focus,
                    b.time_consumption = bk.time_consumption,
                    b.date_added = bk.date_added,
                    b.updated_at = datetime()
            WITH b, bk
            UNWIND bk.topic_names AS topic_name
            MERGE (t:Topic {name: topic_name})
                ON CREATE SET t.created_at = datetime(), t.updated_at = datetime()
                ON MATCH SET t.updated_at = datetime()
            MERGE (b)-[:TAGGED_WITH]->(t)
        """
        summary = await self._write(query, {"bookmarks": bookmarks})
        return summary.counters.nodes_created + summary.counters.properties_set
