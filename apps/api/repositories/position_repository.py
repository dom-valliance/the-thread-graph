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

    async def create_position(self, data: dict[str, object]) -> dict[str, object] | None:
        query = """
            CREATE (p:Position {
                id: $id,
                text: $text,
                status: 'draft',
                version: 1,
                locked_date: null,
                locked_by: null,
                anti_position_text: $anti_position_text,
                cross_arc_bridge_text: $cross_arc_bridge_text,
                p1_v1_mapping: $p1_v1_mapping,
                steelman_addressed: null,
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH p
            MATCH (a:Arc {number: $arc_number})
            CREATE (p)-[:LOCKED_IN]->(a)
            WITH p
            OPTIONAL MATCH (ss:ScheduledSession {id: $session_id})
            FOREACH (_ IN CASE WHEN ss IS NOT NULL THEN [1] ELSE [] END |
                CREATE (p)-[:PRODUCED_IN]->(ss)
            )
            RETURN p {
                .id, .text, .status, .version, .locked_date, .locked_by,
                .anti_position_text, .cross_arc_bridge_text, .p1_v1_mapping,
                .steelman_addressed, .created_at, .updated_at,
                arc_number: $arc_number,
                proposition: null
            } AS position
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["position"]))

    async def update_position(
        self, position_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        set_clauses: list[str] = []
        params: dict[str, object] = {"id": position_id}

        for field in ("text", "anti_position_text", "cross_arc_bridge_text",
                       "p1_v1_mapping", "steelman_addressed"):
            if field in data and data[field] is not None:
                set_clauses.append(f"p.{field} = ${field}")
                params[field] = data[field]

        if not set_clauses:
            return await self.get_position_basic(position_id)

        set_clauses.append("p.updated_at = datetime()")

        query = f"""
            MATCH (p:Position {{id: $id}})
            WHERE p.status IN ['draft', 'under_revision']
            MATCH (p)-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            SET {', '.join(set_clauses)}
            RETURN p {{
                .id, .text, .status, .version, .locked_date, .locked_by,
                .anti_position_text, .cross_arc_bridge_text, .p1_v1_mapping,
                .steelman_addressed, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            }} AS position
        """
        records = await self._write_and_return(query, params)
        if not records:
            return None
        return serialise_record(dict(records[0]["position"]))

    async def get_position_basic(self, position_id: str) -> dict[str, object] | None:
        query = """
            MATCH (p:Position {id: $id})-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            RETURN p {
                .id, .text, .status, .version, .locked_date, .locked_by,
                .anti_position_text, .cross_arc_bridge_text, .p1_v1_mapping,
                .steelman_addressed, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            } AS position
        """
        records = await self._read(query, {"id": position_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["position"]))

    async def lock_position(
        self, position_id: str, locked_by: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (p:Position {id: $id})
            WHERE p.status IN ['draft', 'under_revision']
              AND p.anti_position_text IS NOT NULL
              AND p.cross_arc_bridge_text IS NOT NULL
              AND p.p1_v1_mapping IS NOT NULL
            MATCH (p)-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (p)-[:MAPS_TO]->(pr:Proposition)
            SET p.status = 'locked',
                p.locked_date = datetime(),
                p.locked_by = $locked_by,
                p.updated_at = datetime()
            RETURN p {
                .id, .text, .status, .version, .locked_date, .locked_by,
                .anti_position_text, .cross_arc_bridge_text, .p1_v1_mapping,
                .steelman_addressed, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            } AS position
        """
        records = await self._write_and_return(
            query, {"id": position_id, "locked_by": locked_by}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["position"]))

    async def revise_position(
        self, position_id: str, new_id: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (old:Position {id: $id})
            WHERE old.status = 'locked'
            MATCH (old)-[:LOCKED_IN]->(a:Arc)
            OPTIONAL MATCH (old)-[:MAPS_TO]->(pr:Proposition)
            CREATE (new:Position {
                id: $new_id,
                text: old.text,
                status: 'draft',
                version: old.version + 1,
                locked_date: null,
                locked_by: null,
                anti_position_text: old.anti_position_text,
                cross_arc_bridge_text: old.cross_arc_bridge_text,
                p1_v1_mapping: old.p1_v1_mapping,
                steelman_addressed: old.steelman_addressed,
                created_at: datetime(),
                updated_at: datetime()
            })
            CREATE (new)-[:LOCKED_IN]->(a)
            CREATE (new)-[:SUPERSEDES]->(old)
            FOREACH (_ IN CASE WHEN pr IS NOT NULL THEN [1] ELSE [] END |
                CREATE (new)-[:MAPS_TO]->(pr)
            )
            SET old.status = 'under_revision'
            RETURN new {
                .id, .text, .status, .version, .locked_date, .locked_by,
                .anti_position_text, .cross_arc_bridge_text, .p1_v1_mapping,
                .steelman_addressed, .created_at, .updated_at,
                arc_number: a.number,
                proposition: pr.name
            } AS position
        """
        records = await self._write_and_return(
            query, {"id": position_id, "new_id": new_id}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["position"]))

    async def get_position_versions(
        self, position_id: str
    ) -> list[dict[str, object]]:
        query = """
            MATCH (start:Position {id: $id})
            OPTIONAL MATCH chain = (start)-[:SUPERSEDES*0..]->(older:Position)
            WITH older
            ORDER BY older.version DESC
            RETURN older {
                .id, .text, .version, .status,
                .locked_date, .locked_by,
                .created_at, .updated_at
            } AS version
        """
        records = await self._read(query, {"id": position_id})
        return [serialise_record(dict(record["version"])) for record in records]

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
