from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class PositionRepository(BaseRepository):
    async def list_positions(
        self,
        arc_number: int | None = None,
        status: str | None = None,
        proposition: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[dict[str, object]]:
        """List positions with optional filtering by arc, status, and proposition."""
        where_clauses: list[str] = []
        params: dict[str, object] = {"limit": limit}

        if arc_number is not None:
            where_clauses.append("a.number = $arc_number")
            params["arc_number"] = arc_number

        if status is not None:
            where_clauses.append("p.status = $status")
            params["status"] = status

        if proposition is not None:
            where_clauses.append("pr.name = $proposition")
            params["proposition"] = proposition

        if cursor is not None:
            where_clauses.append("p.id > $cursor")
            params["cursor"] = cursor

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            MATCH (p:Position)-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            {where}
            RETURN p {{
                .id, .text, .status, .locked_date, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            }} AS position
            ORDER BY p.id
            LIMIT $limit
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["position"])) for record in records]

    async def get_position(self, position_id: str) -> dict[str, object] | None:
        """Get a single position with its anti-position, evidence chain, and arguments."""
        # Fetch the position with its arc and proposition
        pos_query = """
            MATCH (p:Position {id: $id})-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            RETURN p {
                .id, .text, .status, .locked_date, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            } AS position
        """
        records = await self._read(pos_query, {"id": position_id})
        if not records:
            return None

        position = serialise_record(dict(records[0]["position"]))

        # Anti-position
        anti_query = """
            MATCH (p:Position {id: $id})-[:HAS_ANTI_POSITION]->(ap:AntiPosition)
            RETURN ap {
                .id, .text,
                position_id: $id,
                .created_at, .updated_at
            } AS anti_position
        """
        anti_records = await self._read(anti_query, {"id": position_id})
        position["anti_position"] = (
            serialise_record(dict(anti_records[0]["anti_position"])) if anti_records else None
        )

        # Evidence chain
        ev_query = """
            MATCH (e:Evidence)-[:SUPPORTS]->(p:Position {id: $id})
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b:Bookmark)
            RETURN e {
                .id, .text, .type,
                source_title: b.title
            } AS evidence
            ORDER BY e.created_at
        """
        ev_records = await self._read(ev_query, {"id": position_id})
        position["evidence_chain"] = [
            serialise_record(dict(record["evidence"])) for record in ev_records
        ]

        # Supporting arguments
        sup_query = """
            MATCH (arg:Argument)-[:SUPPORTS]->(p:Position {id: $id})
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                source_session_id: s.id
            } AS argument
            ORDER BY arg.created_at
        """
        sup_records = await self._read(sup_query, {"id": position_id})
        position["supporting_arguments"] = [
            serialise_record(dict(record["argument"])) for record in sup_records
        ]

        # Challenging arguments
        ch_query = """
            MATCH (arg:Argument)-[:CHALLENGES]->(p:Position {id: $id})
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                source_session_id: s.id
            } AS argument
            ORDER BY arg.created_at
        """
        ch_records = await self._read(ch_query, {"id": position_id})
        position["challenging_arguments"] = [
            serialise_record(dict(record["argument"])) for record in ch_records
        ]

        return position

    async def get_argument_map(self, position_id: str) -> dict[str, object] | None:
        """Get the full argument map for a position."""
        # Fetch base position
        pos_query = """
            MATCH (p:Position {id: $id})-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            RETURN p {
                .id, .text, .status, .locked_date, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            } AS position
        """
        records = await self._read(pos_query, {"id": position_id})
        if not records:
            return None

        result: dict[str, object] = {"position": serialise_record(dict(records[0]["position"]))}

        # Supporting arguments
        sup_query = """
            MATCH (arg:Argument)-[:SUPPORTS]->(p:Position {id: $id})
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                source_session_id: s.id
            } AS argument
        """
        sup_records = await self._read(sup_query, {"id": position_id})
        result["supporting"] = [
            serialise_record(dict(record["argument"])) for record in sup_records
        ]

        # Challenging arguments
        ch_query = """
            MATCH (arg:Argument)-[:CHALLENGES]->(p:Position {id: $id})
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                source_session_id: s.id
            } AS argument
        """
        ch_records = await self._read(ch_query, {"id": position_id})
        result["challenging"] = [
            serialise_record(dict(record["argument"])) for record in ch_records
        ]

        # Steelman arguments
        steel_query = """
            MATCH (p:Position {id: $id})-[:LOCKED_IN]->(a:Arc)-[:HAS_STEELMAN]->(sa:SteelmanArgument)
            RETURN sa { .id, .text } AS steelman
        """
        steel_records = await self._read(steel_query, {"id": position_id})
        result["steelman"] = [
            serialise_record(dict(record["steelman"])) for record in steel_records
        ]

        # Objection-response pairs
        obj_query = """
            MATCH (p:Position {id: $id})<-[:OBJECTS_TO]-(op:ObjectionPair)
            RETURN op {
                .id, .objection_text, .response_text
            } AS objection_pair
        """
        obj_records = await self._read(obj_query, {"id": position_id})
        result["objection_pairs"] = [
            serialise_record(dict(record["objection_pair"])) for record in obj_records
        ]

        return result

    async def get_evidence_trail(
        self, position_id: str
    ) -> dict[str, object] | None:
        """Get the evidence provenance trail for a position.

        Returns the position with its full evidence chain, including
        source bookmarks and their arc membership.
        """
        pos_query = """
            MATCH (p:Position {id: $id})
            RETURN p { .id, .text, .status } AS position
        """
        records = await self._read(pos_query, {"id": position_id})
        if not records:
            return None

        position = serialise_record(dict(records[0]["position"]))

        trail_query = """
            MATCH (e:Evidence)-[:SUPPORTS]->(p:Position {id: $id})
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b:Bookmark)
            OPTIONAL MATCH (b)-[:BELONGS_TO_ARC]->(a:Arc)
            WITH e, b, collect(DISTINCT a.name) AS bookmark_arc_names
            RETURN e {
                .id, .text, .type,
                source_bookmark: CASE WHEN b IS NOT NULL THEN b {
                    .notion_id, .title, .url, .source,
                    .edge_or_foundational, .ai_summary,
                    arc_names: bookmark_arc_names
                } ELSE null END
            } AS evidence
            ORDER BY e.created_at
        """
        trail_records = await self._read(trail_query, {"id": position_id})
        evidence = [
            serialise_record(dict(record["evidence"]))
            for record in trail_records
        ]

        return {
            "position_id": position["id"],
            "position_text": position["text"],
            "evidence": evidence,
        }

    async def get_changes_since_lock(
        self, position_id: str
    ) -> dict[str, object] | None:
        """Get evidence and arguments added after the position's locked_date."""
        # Verify position exists and has a locked date
        pos_query = """
            MATCH (p:Position {id: $id})
            RETURN p.locked_date AS locked_date
        """
        records = await self._read(pos_query, {"id": position_id})
        if not records:
            return None

        locked_date = records[0]["locked_date"]
        if locked_date is None:
            return {"new_evidence": [], "new_arguments": []}

        # Evidence added after lock
        ev_query = """
            MATCH (e:Evidence)-[:SUPPORTS]->(p:Position {id: $id})
            WHERE e.created_at > $locked_date
            OPTIONAL MATCH (e)-[:SOURCED_FROM]->(b:Bookmark)
            RETURN e {
                .id, .text, .type,
                source_title: b.title
            } AS evidence
            ORDER BY e.created_at
        """
        ev_records = await self._read(
            ev_query, {"id": position_id, "locked_date": locked_date}
        )

        # Arguments added after lock
        arg_query = """
            MATCH (arg:Argument)-[:SUPPORTS|CHALLENGES]->(p:Position {id: $id})
            WHERE arg.created_at > $locked_date
            OPTIONAL MATCH (arg)-[:MADE_IN]->(s:Session)
            RETURN arg {
                .id, .text, .sentiment, .strength, .speaker,
                source_session_id: s.id
            } AS argument
            ORDER BY arg.created_at
        """
        arg_records = await self._read(
            arg_query, {"id": position_id, "locked_date": locked_date}
        )

        return {
            "new_evidence": [serialise_record(dict(r["evidence"])) for r in ev_records],
            "new_arguments": [serialise_record(dict(r["argument"])) for r in arg_records],
        }
