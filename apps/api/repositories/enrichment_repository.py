from __future__ import annotations

from repositories.base import BaseRepository


class EnrichmentRepository(BaseRepository):
    async def batch_create_arguments(
        self, arguments: list[dict[str, object]]
    ) -> dict[str, int]:
        """MERGE arguments and create relationships to positions and sessions."""
        query = """
            UNWIND $items AS item
            MERGE (a:Argument {id: item.id})
            ON CREATE SET
                a.text = item.text,
                a.sentiment = item.sentiment,
                a.strength = item.strength,
                a.speaker = item.speaker,
                a.created_at = datetime(),
                a.updated_at = datetime()
            ON MATCH SET
                a.text = item.text,
                a.sentiment = item.sentiment,
                a.strength = item.strength,
                a.speaker = item.speaker,
                a.updated_at = datetime()
            WITH a, item
            FOREACH (_ IN CASE WHEN item.position_id IS NOT NULL AND item.relationship_type = 'supports' THEN [1] ELSE [] END |
                MERGE (p:Position {id: item.position_id})
                MERGE (a)-[:SUPPORTS]->(p)
            )
            FOREACH (_ IN CASE WHEN item.position_id IS NOT NULL AND item.relationship_type = 'challenges' THEN [1] ELSE [] END |
                MERGE (p:Position {id: item.position_id})
                MERGE (a)-[:CHALLENGES]->(p)
            )
            FOREACH (_ IN CASE WHEN item.session_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (s:Session {id: item.session_id})
                MERGE (a)-[:MADE_IN]->(s)
            )
            RETURN
                sum(CASE WHEN a.created_at = a.updated_at THEN 1 ELSE 0 END) AS created_count,
                sum(CASE WHEN a.created_at <> a.updated_at THEN 1 ELSE 0 END) AS updated_count
        """
        records = await self._read(query, {"items": arguments})
        if not records:
            return {"created_count": 0, "updated_count": 0}
        return {
            "created_count": records[0]["created_count"],
            "updated_count": records[0]["updated_count"],
        }

    async def batch_create_action_items(
        self, items: list[dict[str, object]]
    ) -> dict[str, int]:
        """MERGE action items and create GENERATED relationships to sessions."""
        query = """
            UNWIND $items AS item
            MERGE (ai:ActionItem {id: item.id})
            ON CREATE SET
                ai.text = item.text,
                ai.assignee = item.assignee,
                ai.due_date = item.due_date,
                ai.created_at = datetime(),
                ai.updated_at = datetime()
            ON MATCH SET
                ai.text = item.text,
                ai.assignee = item.assignee,
                ai.due_date = item.due_date,
                ai.updated_at = datetime()
            WITH ai, item
            FOREACH (_ IN CASE WHEN item.session_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (s:Session {id: item.session_id})
                MERGE (ai)-[:GENERATED]->(s)
            )
            RETURN
                sum(CASE WHEN ai.created_at = ai.updated_at THEN 1 ELSE 0 END) AS created_count,
                sum(CASE WHEN ai.created_at <> ai.updated_at THEN 1 ELSE 0 END) AS updated_count
        """
        records = await self._read(query, {"items": items})
        if not records:
            return {"created_count": 0, "updated_count": 0}
        return {
            "created_count": records[0]["created_count"],
            "updated_count": records[0]["updated_count"],
        }

    async def batch_create_evidence(
        self, evidence: list[dict[str, object]]
    ) -> dict[str, int]:
        """MERGE evidence and create relationships to positions and bookmarks."""
        query = """
            UNWIND $items AS item
            MERGE (e:Evidence {id: item.id})
            ON CREATE SET
                e.text = item.text,
                e.type = item.type,
                e.created_at = datetime(),
                e.updated_at = datetime()
            ON MATCH SET
                e.text = item.text,
                e.type = item.type,
                e.updated_at = datetime()
            WITH e, item
            FOREACH (_ IN CASE WHEN item.position_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (p:Position {id: item.position_id})
                MERGE (e)-[:SUPPORTS]->(p)
            )
            FOREACH (_ IN CASE WHEN item.source_bookmark_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (b:Bookmark {id: item.source_bookmark_id})
                MERGE (e)-[:SOURCED_FROM]->(b)
            )
            RETURN
                sum(CASE WHEN e.created_at = e.updated_at THEN 1 ELSE 0 END) AS created_count,
                sum(CASE WHEN e.created_at <> e.updated_at THEN 1 ELSE 0 END) AS updated_count
        """
        records = await self._read(query, {"items": evidence})
        if not records:
            return {"created_count": 0, "updated_count": 0}
        return {
            "created_count": records[0]["created_count"],
            "updated_count": records[0]["updated_count"],
        }
