from __future__ import annotations

from repositories.base import BaseRepository


class SyncRepository(BaseRepository):
    async def upsert_bookmarks(
        self, bookmarks: list[dict[str, object]]
    ) -> dict[str, int]:
        """MERGE bookmarks on notion_id, creating topics and theme relationships."""
        query = """
            UNWIND $items AS item
            MERGE (b:Bookmark {notion_id: item.notion_id})
            ON CREATE SET
                b.title = item.title,
                b.source = item.source,
                b.url = item.url,
                b.ai_summary = item.ai_summary,
                b.valliance_viewpoint = item.valliance_viewpoint,
                b.edge_or_foundational = item.edge_or_foundational,
                b.focus = item.focus,
                b.time_consumption = item.time_consumption,
                b.date_added = item.date_added,
                b.created_at = datetime(),
                b.updated_at = datetime()
            ON MATCH SET
                b.title = item.title,
                b.source = item.source,
                b.url = item.url,
                b.ai_summary = item.ai_summary,
                b.valliance_viewpoint = item.valliance_viewpoint,
                b.edge_or_foundational = item.edge_or_foundational,
                b.focus = item.focus,
                b.time_consumption = item.time_consumption,
                b.date_added = item.date_added,
                b.updated_at = datetime()
            WITH b, item
            FOREACH (topic_name IN item.topic_names |
                MERGE (t:Topic {name: topic_name})
                ON CREATE SET t.created_at = datetime(), t.updated_at = datetime()
                MERGE (b)-[:TAGGED_WITH]->(t)
            )
            FOREACH (_ IN CASE WHEN item.theme_name IS NOT NULL THEN [1] ELSE [] END |
                MERGE (th:Theme {name: item.theme_name})
                ON CREATE SET th.created_at = datetime(), th.updated_at = datetime()
                MERGE (b)-[:HAS_THEME]->(th)
            )
            RETURN
                sum(CASE WHEN b.created_at = b.updated_at THEN 1 ELSE 0 END) AS created_count,
                sum(CASE WHEN b.created_at <> b.updated_at THEN 1 ELSE 0 END) AS updated_count
        """
        records = await self._write_and_return(query, {"items": bookmarks})
        if not records:
            return {"created_count": 0, "updated_count": 0}
        return {
            "created_count": records[0]["created_count"],
            "updated_count": records[0]["updated_count"],
        }

    async def upsert_sessions(
        self, sessions: list[dict[str, object]]
    ) -> dict[str, int]:
        """MERGE sessions on notion_id, creating arc relationships."""
        query = """
            UNWIND $items AS item
            MERGE (s:Session {notion_id: item.notion_id})
            ON CREATE SET
                s.title = item.title,
                s.date = item.date,
                s.duration = item.duration,
                s.summary = item.summary,
                s.transcript = item.transcript,
                s.created_at = datetime(),
                s.updated_at = datetime()
            ON MATCH SET
                s.title = item.title,
                s.date = item.date,
                s.duration = item.duration,
                s.summary = item.summary,
                s.transcript = item.transcript,
                s.updated_at = datetime()
            WITH s, item
            FOREACH (_ IN CASE WHEN item.theme_name IS NOT NULL THEN [1] ELSE [] END |
                MERGE (th:Theme {name: item.theme_name})
                ON CREATE SET th.created_at = datetime(), th.updated_at = datetime()
                MERGE (s)-[:HAS_THEME]->(th)
            )
            RETURN
                sum(CASE WHEN s.created_at = s.updated_at THEN 1 ELSE 0 END) AS created_count,
                sum(CASE WHEN s.created_at <> s.updated_at THEN 1 ELSE 0 END) AS updated_count
        """
        records = await self._write_and_return(query, {"items": sessions})
        if not records:
            return {"created_count": 0, "updated_count": 0}
        return {
            "created_count": records[0]["created_count"],
            "updated_count": records[0]["updated_count"],
        }
