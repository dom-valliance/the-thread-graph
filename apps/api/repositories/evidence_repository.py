from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class EvidenceRepository(BaseRepository):
    async def list_evidence(
        self,
        position_id: str | None = None,
        type: str | None = None,
    ) -> list[dict[str, object]]:
        """List evidence with optional filtering by position and type."""
        where_clauses: list[str] = []
        params: dict[str, object] = {}

        if position_id is not None:
            where_clauses.append("p.id = $position_id")
            params["position_id"] = position_id

        if type is not None:
            where_clauses.append("e.type = $type")
            params["type"] = type

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        position_match = (
            "MATCH (e)-[:SUPPORTS]->(p:Position)"
            if position_id is not None
            else "OPTIONAL MATCH (e)-[:SUPPORTS]->(p:Position)"
        )

        query = f"""
            MATCH (e:Evidence)
            {position_match}
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b:Bookmark)
            {where}
            RETURN e {{
                .id, .text, .type, .created_at, .updated_at,
                source_id: b.id,
                source_title: b.title,
                position_id: p.id
            }} AS evidence
            ORDER BY e.created_at DESC
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["evidence"])) for record in records]

    async def get_evidence(self, evidence_id: str) -> dict[str, object] | None:
        """Get a single evidence node with its source and position."""
        query = """
            MATCH (e:Evidence {id: $id})
            OPTIONAL MATCH (e)-[:SUPPORTS]->(p:Position)
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b:Bookmark)
            RETURN e {
                .id, .text, .type, .created_at, .updated_at,
                source_id: b.id,
                source_title: b.title,
                position_id: p.id
            } AS evidence
        """
        records = await self._read(query, {"id": evidence_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["evidence"]))

    async def create_evidence(
        self, data: dict[str, object]
    ) -> dict[str, object] | None:
        """Create a single evidence node linked to a position.

        Optionally links to a source bookmark via SOURCED_FROM.
        """
        query = """
            MATCH (p:Position {id: $position_id})
            CREATE (e:Evidence {
                id: $id,
                text: $text,
                type: $type,
                created_at: datetime(),
                updated_at: datetime()
            })
            CREATE (e)-[:SUPPORTS]->(p)
            WITH e
            OPTIONAL MATCH (b:Bookmark {notion_id: $source_bookmark_id})
            FOREACH (_ IN CASE WHEN b IS NOT NULL THEN [1] ELSE [] END |
                CREATE (e)-[:SOURCED_FROM]->(b)
            )
            RETURN e {
                .id, .text, .type, .created_at, .updated_at,
                position_id: $position_id,
                source_id: $source_bookmark_id
            } AS evidence
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["evidence"]))

    async def update_evidence(
        self, evidence_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        """Update evidence text, type, and optionally re-link source bookmark."""
        query = """
            MATCH (e:Evidence {id: $id})
            SET e.text = $text, e.type = $type, e.updated_at = datetime()
            WITH e
            OPTIONAL MATCH (e)-[old_source:SOURCED_FROM]->()
            DELETE old_source
            WITH e
            OPTIONAL MATCH (b:Bookmark {notion_id: $source_bookmark_id})
            FOREACH (_ IN CASE WHEN b IS NOT NULL THEN [1] ELSE [] END |
                CREATE (e)-[:SOURCED_FROM]->(b)
            )
            WITH e
            OPTIONAL MATCH (e)-[:SUPPORTS]->(p:Position)
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b2:Bookmark)
            RETURN e {
                .id, .text, .type, .created_at, .updated_at,
                source_id: b2.id,
                source_title: b2.title,
                position_id: p.id
            } AS evidence
        """
        records = await self._write_and_return(
            query, {"id": evidence_id, **data}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["evidence"]))

    async def delete_evidence(self, evidence_id: str) -> bool:
        """Delete an evidence node and its relationships."""
        query = """
            MATCH (e:Evidence {id: $id})
            DETACH DELETE e
        """
        summary = await self._write(query, {"id": evidence_id})
        return summary.counters.nodes_deleted > 0

    async def batch_create_evidence(
        self, evidence_list: list[dict[str, object]]
    ) -> int:
        """Create or update evidence nodes in bulk using MERGE for idempotence.

        Returns the number of nodes created.
        """
        query = """
            UNWIND $evidence_list AS ev
            MERGE (e:Evidence {id: ev.id})
            ON CREATE SET
                e.text = ev.text,
                e.type = ev.type,
                e.created_at = datetime(),
                e.updated_at = datetime()
            ON MATCH SET
                e.text = ev.text,
                e.type = ev.type,
                e.updated_at = datetime()
            WITH e, ev
            FOREACH (_ IN CASE WHEN ev.position_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (p:Position {id: ev.position_id})
                MERGE (e)-[:SUPPORTS]->(p)
            )
            FOREACH (_ IN CASE WHEN ev.source_id IS NOT NULL THEN [1] ELSE [] END |
                MERGE (b:Bookmark {id: ev.source_id})
                MERGE (e)-[:SOURCED_FROM]->(b)
            )
        """
        summary = await self._write(query, {"evidence_list": evidence_list})
        return summary.counters.nodes_created
