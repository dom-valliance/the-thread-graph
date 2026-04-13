from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class CycleRepository(BaseRepository):
    async def list_cycles(self) -> list[dict[str, object]]:
        query = """
            MATCH (c:Cycle)
            RETURN c {
                .id, .number, .start_date, .end_date,
                .status, .created_at, .updated_at
            } AS cycle
            ORDER BY c.number DESC
        """
        records = await self._read(query)
        return [serialise_record(dict(record["cycle"])) for record in records]

    async def get_cycle(self, cycle_id: str) -> dict[str, object] | None:
        query = """
            MATCH (c:Cycle {id: $cycle_id})
            RETURN c {
                .id, .number, .start_date, .end_date,
                .status, .created_at, .updated_at
            } AS cycle
        """
        records = await self._read(query, {"cycle_id": cycle_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["cycle"]))

    async def get_current_cycle(self) -> dict[str, object] | None:
        """Get the active cycle with its current or next scheduled session."""
        query = """
            MATCH (c:Cycle {status: 'active'})
            OPTIONAL MATCH (ss:ScheduledSession)-[:PART_OF]->(c)
            OPTIONAL MATCH (ss)-[:COVERS]->(a:Arc)
            OPTIONAL MATCH (lead:Person)-[:LEADS]->(ss)
            OPTIONAL MATCH (shadow:Person)-[:SHADOWS]->(ss)
            WITH c, ss, a, lead, shadow
            ORDER BY ss.week_number
            WITH c, collect({
                id: ss.id,
                cycle_number: ss.cycle_number,
                week_number: ss.week_number,
                arc_number: ss.arc_number,
                arc_name: a.name,
                week_type: ss.week_type,
                date: ss.date,
                status: ss.status,
                lead_name: lead.name,
                lead_email: lead.email,
                shadow_name: shadow.name,
                shadow_email: shadow.email,
                created_at: ss.created_at,
                updated_at: ss.updated_at
            }) AS sessions
            WITH c, sessions,
                 [s IN sessions WHERE s.date >= date() | s] AS upcoming,
                 [s IN sessions WHERE s.status = 'in_progress' | s] AS in_progress
            WITH c, sessions,
                 CASE
                     WHEN size(in_progress) > 0 THEN in_progress[0]
                     WHEN size(upcoming) > 0 THEN upcoming[0]
                     ELSE null
                 END AS current_session,
                 CASE
                     WHEN size(upcoming) > 0
                     THEN duration.inDays(date(), upcoming[0].date).days
                     ELSE null
                 END AS days_until_next
            RETURN c {
                .id, .number, .start_date, .end_date,
                .status, .created_at, .updated_at
            } AS cycle,
            current_session,
            days_until_next
        """
        records = await self._read(query)
        if not records:
            return None
        record = records[0]
        result = serialise_record(dict(record["cycle"]))
        current = record["current_session"]
        if current is not None:
            result["current_session"] = serialise_record(dict(current))
        else:
            result["current_session"] = None
        result["days_until_next"] = record["days_until_next"]
        return result

    async def create_cycle(
        self,
        cycle_id: str,
        number: int,
        start_date: str,
        end_date: str,
        status: str,
        sessions: list[dict[str, object]],
    ) -> dict[str, object] | None:
        """Create a cycle and its 12 scheduled sessions."""
        query = """
            MERGE (c:Cycle {id: $cycle_id})
            ON CREATE SET
                c.number = $number,
                c.start_date = date($start_date),
                c.end_date = date($end_date),
                c.status = $status,
                c.created_at = datetime(),
                c.updated_at = datetime()
            ON MATCH SET
                c.updated_at = datetime()
            WITH c
            UNWIND $sessions AS ss
            MERGE (s:ScheduledSession {id: ss.id})
            ON CREATE SET
                s.cycle_number = ss.cycle_number,
                s.week_number = ss.week_number,
                s.arc_number = ss.arc_number,
                s.week_type = ss.week_type,
                s.date = date(ss.date),
                s.status = 'upcoming',
                s.created_at = datetime(),
                s.updated_at = datetime()
            ON MATCH SET
                s.updated_at = datetime()
            MERGE (s)-[:PART_OF]->(c)
            WITH s, ss
            MATCH (a:Arc {number: ss.arc_number})
            MERGE (s)-[:COVERS]->(a)
            WITH s
            ORDER BY s.week_number
            WITH collect(s) AS all_sessions
            MATCH (c:Cycle {id: $cycle_id})
            RETURN c {
                .id, .number, .start_date, .end_date,
                .status, .created_at, .updated_at
            } AS cycle
        """
        records = await self._write_and_return(query, {
            "cycle_id": cycle_id,
            "number": number,
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "sessions": sessions,
        })
        if not records:
            return None
        return serialise_record(dict(records[0]["cycle"]))

    async def get_cycle_schedule(
        self, cycle_id: str
    ) -> tuple[dict[str, object] | None, list[dict[str, object]]]:
        """Get a cycle and all its scheduled sessions."""
        query = """
            MATCH (c:Cycle {id: $cycle_id})
            OPTIONAL MATCH (ss:ScheduledSession)-[:PART_OF]->(c)
            OPTIONAL MATCH (ss)-[:COVERS]->(a:Arc)
            OPTIONAL MATCH (lead:Person)-[:LEADS]->(ss)
            OPTIONAL MATCH (shadow:Person)-[:SHADOWS]->(ss)
            WITH c, ss {
                .id, .cycle_number, .week_number, .arc_number,
                .week_type, .date, .status, .created_at, .updated_at,
                arc_name: a.name,
                lead_name: lead.name,
                lead_email: lead.email,
                shadow_name: shadow.name,
                shadow_email: shadow.email
            } AS session
            ORDER BY session.week_number
            RETURN c {
                .id, .number, .start_date, .end_date,
                .status, .created_at, .updated_at
            } AS cycle,
            collect(session) AS sessions
        """
        records = await self._read(query, {"cycle_id": cycle_id})
        if not records:
            return None, []
        record = records[0]
        cycle = serialise_record(dict(record["cycle"]))
        sessions = [serialise_record(dict(s)) for s in record["sessions"] if s.get("id")]
        return cycle, sessions

    async def update_session_assignment(
        self,
        session_id: str,
        lead_email: str | None,
        shadow_email: str | None,
    ) -> dict[str, object] | None:
        """Update lead/shadow assignment for a scheduled session."""
        query = """
            MATCH (ss:ScheduledSession {id: $session_id})
            OPTIONAL MATCH (ss)<-[old_lead:LEADS]-()
            DELETE old_lead
            WITH ss
            OPTIONAL MATCH (ss)<-[old_shadow:SHADOWS]-()
            DELETE old_shadow
            WITH ss
            OPTIONAL MATCH (lead:Person {email: $lead_email})
            FOREACH (_ IN CASE WHEN lead IS NOT NULL THEN [1] ELSE [] END |
                MERGE (lead)-[:LEADS]->(ss)
            )
            WITH ss
            OPTIONAL MATCH (shadow:Person {email: $shadow_email})
            FOREACH (_ IN CASE WHEN shadow IS NOT NULL THEN [1] ELSE [] END |
                MERGE (shadow)-[:SHADOWS]->(ss)
            )
            WITH ss
            SET ss.updated_at = datetime()
            OPTIONAL MATCH (ss)-[:COVERS]->(a:Arc)
            OPTIONAL MATCH (lead2:Person)-[:LEADS]->(ss)
            OPTIONAL MATCH (shadow2:Person)-[:SHADOWS]->(ss)
            RETURN ss {
                .id, .cycle_number, .week_number, .arc_number,
                .week_type, .date, .status, .created_at, .updated_at,
                arc_name: a.name,
                lead_name: lead2.name,
                lead_email: lead2.email,
                shadow_name: shadow2.name,
                shadow_email: shadow2.email
            } AS session
        """
        records = await self._write_and_return(query, {
            "session_id": session_id,
            "lead_email": lead_email,
            "shadow_email": shadow_email,
        })
        if not records:
            return None
        return serialise_record(dict(records[0]["session"]))

    async def get_scheduled_session(
        self, session_id: str
    ) -> dict[str, object] | None:
        """Get a single scheduled session by ID."""
        query = """
            MATCH (ss:ScheduledSession {id: $session_id})
            OPTIONAL MATCH (ss)-[:COVERS]->(a:Arc)
            OPTIONAL MATCH (lead:Person)-[:LEADS]->(ss)
            OPTIONAL MATCH (shadow:Person)-[:SHADOWS]->(ss)
            RETURN ss {
                .id, .cycle_number, .week_number, .arc_number,
                .week_type, .date, .status, .created_at, .updated_at,
                arc_name: a.name,
                lead_name: lead.name,
                lead_email: lead.email,
                shadow_name: shadow.name,
                shadow_email: shadow.email
            } AS session
        """
        records = await self._read(query, {"session_id": session_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["session"]))
