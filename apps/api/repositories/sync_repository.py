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
            FOREACH (arc_name IN item.arc_bucket_names |
                MERGE (a:Arc {name: arc_name})
                ON CREATE SET a.created_at = datetime(), a.updated_at = datetime()
                MERGE (b)-[:BELONGS_TO_ARC]->(a)
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
        """MERGE discussion recordings on notion_id.

        Links each recording to its parent bookmark via DISCUSSED_IN.
        Arc membership is derived from the bookmark's BELONGS_TO_ARC relationship.
        """
        query = """
            UNWIND $items AS item
            MERGE (s:Session {notion_id: item.notion_id})
            ON CREATE SET
                s.title = item.title,
                s.date = item.date,
                s.ai_suggested_viewpoint = item.ai_suggested_viewpoint,
                s.created_at = datetime(),
                s.updated_at = datetime()
            ON MATCH SET
                s.title = item.title,
                s.date = item.date,
                s.ai_suggested_viewpoint = item.ai_suggested_viewpoint,
                s.updated_at = datetime()
            WITH s, item
            FOREACH (_ IN CASE WHEN item.bookmark_notion_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (b:Bookmark {notion_id: item.bookmark_notion_id})
                MERGE (b)-[:DISCUSSED_IN]->(s)
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
