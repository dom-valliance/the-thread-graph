from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class PrepRepository(BaseRepository):
    async def create_workshop_assignment(
        self, data: dict[str, object]
    ) -> dict[str, object] | None:
        query = """
            CREATE (wa:WorkshopAssignment {
                id: $id,
                player_or_approach: $player_or_approach,
                analysis_notes: null,
                status: 'assigned',
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH wa
            MATCH (person:Person {email: $assigned_to_email})
            CREATE (wa)-[:ASSIGNED_TO]->(person)
            WITH wa, person
            MATCH (ss:ScheduledSession {id: $session_id})
            CREATE (wa)-[:FOR_SESSION]->(ss)
            WITH wa, person
            OPTIONAL MATCH (pl:Player {name: $player_or_approach})
            FOREACH (_ IN CASE WHEN pl IS NOT NULL THEN [1] ELSE [] END |
                CREATE (wa)-[:RESEARCHES]->(pl)
            )
            RETURN wa {
                .id, .player_or_approach, .analysis_notes, .status,
                .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                player_name: pl.name
            } AS assignment
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def list_workshop_assignments(
        self, session_id: str
    ) -> list[dict[str, object]]:
        query = """
            MATCH (wa:WorkshopAssignment)-[:FOR_SESSION]->(ss:ScheduledSession {id: $session_id})
            OPTIONAL MATCH (wa)-[:ASSIGNED_TO]->(person:Person)
            OPTIONAL MATCH (wa)-[:RESEARCHES]->(pl:Player)
            RETURN wa {
                .id, .player_or_approach, .analysis_notes, .status,
                .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                player_name: pl.name
            } AS assignment
            ORDER BY wa.created_at
        """
        records = await self._read(query, {"session_id": session_id})
        return [serialise_record(dict(record["assignment"])) for record in records]

    async def update_workshop_assignment(
        self, assignment_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        set_clauses: list[str] = ["wa.updated_at = datetime()"]
        params: dict[str, object] = {"id": assignment_id}

        if "status" in data and data["status"] is not None:
            set_clauses.append("wa.status = $status")
            params["status"] = data["status"]
        if "analysis_notes" in data and data["analysis_notes"] is not None:
            set_clauses.append("wa.analysis_notes = $analysis_notes")
            params["analysis_notes"] = data["analysis_notes"]

        query = f"""
            MATCH (wa:WorkshopAssignment {{id: $id}})
            OPTIONAL MATCH (wa)-[:ASSIGNED_TO]->(person:Person)
            OPTIONAL MATCH (wa)-[:RESEARCHES]->(pl:Player)
            SET {', '.join(set_clauses)}
            RETURN wa {{
                .id, .player_or_approach, .analysis_notes, .status,
                .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                player_name: pl.name
            }} AS assignment
        """
        records = await self._write_and_return(query, params)
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def create_reading_assignment(
        self, data: dict[str, object]
    ) -> dict[str, object] | None:
        query = """
            CREATE (ra:ReadingAssignment {
                id: $id,
                status: 'assigned',
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH ra
            MATCH (person:Person {email: $assigned_to_email})
            CREATE (ra)-[:ASSIGNED_TO]->(person)
            WITH ra, person
            MATCH (ss:ScheduledSession {id: $session_id})
            CREATE (ra)-[:FOR_SESSION]->(ss)
            WITH ra, person
            MATCH (b:Bookmark {notion_id: $bookmark_notion_id})
            CREATE (ra)-[:COVERS]->(b)
            RETURN ra {
                .id, .status, .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                bookmark_title: b.title,
                bookmark_notion_id: b.notion_id
            } AS assignment
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def list_reading_assignments(
        self, session_id: str
    ) -> list[dict[str, object]]:
        query = """
            MATCH (ra:ReadingAssignment)-[:FOR_SESSION]->(ss:ScheduledSession {id: $session_id})
            OPTIONAL MATCH (ra)-[:ASSIGNED_TO]->(person:Person)
            OPTIONAL MATCH (ra)-[:COVERS]->(b:Bookmark)
            RETURN ra {
                .id, .status, .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                bookmark_title: b.title,
                bookmark_notion_id: b.notion_id
            } AS assignment
            ORDER BY ra.created_at
        """
        records = await self._read(query, {"session_id": session_id})
        return [serialise_record(dict(record["assignment"])) for record in records]

    async def update_reading_assignment(
        self, assignment_id: str, status: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (ra:ReadingAssignment {id: $id})
            OPTIONAL MATCH (ra)-[:ASSIGNED_TO]->(person:Person)
            OPTIONAL MATCH (ra)-[:COVERS]->(b:Bookmark)
            SET ra.status = $status, ra.updated_at = datetime()
            RETURN ra {
                .id, .status, .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                bookmark_title: b.title,
                bookmark_notion_id: b.notion_id
            } AS assignment
        """
        records = await self._write_and_return(
            query, {"id": assignment_id, "status": status}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def get_prep_brief(
        self, session_id: str
    ) -> dict[str, object] | None:
        """Auto-generate a prep brief for a session.

        Pulls: arc name, recent bookmarks for the arc (added since
        previous session), previous cycle's locked position, and
        evidence count.
        """
        query = """
            MATCH (ss:ScheduledSession {id: $session_id})-[:COVERS]->(a:Arc)
            OPTIONAL MATCH (prev:ScheduledSession)-[:COVERS]->(a)
            WHERE prev.week_number < ss.week_number
            WITH ss, a, max(prev.date) AS prev_date

            OPTIONAL MATCH (b:Bookmark)-[:BELONGS_TO_ARC]->(a)
            WHERE prev_date IS NULL OR b.date_added > prev_date
            WITH ss, a, prev_date, collect(b { .notion_id, .title, .url, .date_added })[..20] AS recent_bookmarks

            OPTIONAL MATCH (p:Position {status: 'locked'})-[:LOCKED_IN]->(a)
            WITH ss, a, recent_bookmarks, p
            ORDER BY p.locked_date DESC
            WITH ss, a, recent_bookmarks, head(collect(p.text)) AS prev_position_text

            OPTIONAL MATCH (e:Evidence)-[:SUPPORTS]->(lp:Position)-[:LOCKED_IN]->(a)
            WITH ss, a, recent_bookmarks, prev_position_text, count(e) AS evidence_count

            RETURN ss.id AS session_id,
                   a.name AS arc_name,
                   recent_bookmarks,
                   prev_position_text AS previous_locked_position_text,
                   evidence_count
        """
        records = await self._read(query, {"session_id": session_id})
        if not records:
            return None
        record = records[0]
        return {
            "session_id": record["session_id"],
            "arc_name": record["arc_name"],
            "recent_bookmarks": [
                serialise_record(dict(b)) for b in record["recent_bookmarks"] if b.get("notion_id")
            ],
            "previous_locked_position_text": record["previous_locked_position_text"],
            "evidence_count": record["evidence_count"],
        }
