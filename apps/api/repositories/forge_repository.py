from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class ForgeRepository(BaseRepository):
    async def create_assignment(
        self, data: dict[str, object]
    ) -> dict[str, object] | None:
        query = """
            CREATE (fa:ForgeAssignment {
                id: $id,
                artefact_type: $artefact_type,
                status: 'assigned',
                deadline: date($deadline),
                storyboard_notes: $storyboard_notes,
                published_url: null,
                editor_notes: null,
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH fa
            MATCH (person:Person {email: $assigned_to_email})
            CREATE (fa)-[:ASSIGNED_TO]->(person)
            WITH fa, person
            OPTIONAL MATCH (ss:ScheduledSession {id: $session_id})
            FOREACH (_ IN CASE WHEN ss IS NOT NULL THEN [1] ELSE [] END |
                CREATE (fa)-[:FOR_SESSION]->(ss)
            )
            WITH fa, person
            OPTIONAL MATCH (a:Arc {name: $arc_name})
            FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
                CREATE (fa)-[:FOR_ARC]->(a)
            )
            WITH fa, person
            OPTIONAL MATCH (derived {id: $derived_from_id})
            FOREACH (_ IN CASE WHEN derived IS NOT NULL THEN [1] ELSE [] END |
                CREATE (fa)-[:DERIVED_FROM]->(derived)
            )
            RETURN fa {
                .id, .artefact_type, .status, .deadline,
                .storyboard_notes, .published_url, .editor_notes,
                .created_at, .updated_at,
                assigned_to_name: person.name,
                assigned_to_email: person.email,
                session_id: $session_id,
                arc_name: $arc_name,
                editor_name: null,
                editor_email: null
            } AS assignment
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def list_assignments(
        self,
        status: str | None = None,
        arc: str | None = None,
        person_email: str | None = None,
        cycle_id: str | None = None,
    ) -> list[dict[str, object]]:
        where_clauses: list[str] = []
        params: dict[str, object] = {}

        if status is not None:
            where_clauses.append("fa.status = $status")
            params["status"] = status

        if arc is not None:
            where_clauses.append("a.name = $arc")
            params["arc"] = arc

        if person_email is not None:
            where_clauses.append("assignee.email = $person_email")
            params["person_email"] = person_email

        if cycle_id is not None:
            where_clauses.append("c.id = $cycle_id")
            params["cycle_id"] = cycle_id

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            MATCH (fa:ForgeAssignment)
            OPTIONAL MATCH (fa)-[:ASSIGNED_TO]->(assignee:Person)
            OPTIONAL MATCH (fa)-[:EDITED_BY]->(editor:Person)
            OPTIONAL MATCH (fa)-[:FOR_ARC]->(a:Arc)
            OPTIONAL MATCH (fa)-[:FOR_SESSION]->(ss:ScheduledSession)-[:PART_OF]->(c:Cycle)
            {where}
            RETURN fa {{
                .id, .artefact_type, .status, .deadline,
                .storyboard_notes, .published_url, .editor_notes,
                .created_at, .updated_at,
                assigned_to_name: assignee.name,
                assigned_to_email: assignee.email,
                editor_name: editor.name,
                editor_email: editor.email,
                session_id: ss.id,
                arc_name: a.name
            }} AS assignment
            ORDER BY fa.deadline
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["assignment"])) for record in records]

    async def get_assignment(
        self, assignment_id: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (fa:ForgeAssignment {id: $id})
            OPTIONAL MATCH (fa)-[:ASSIGNED_TO]->(assignee:Person)
            OPTIONAL MATCH (fa)-[:EDITED_BY]->(editor:Person)
            OPTIONAL MATCH (fa)-[:FOR_ARC]->(a:Arc)
            OPTIONAL MATCH (fa)-[:FOR_SESSION]->(ss:ScheduledSession)
            RETURN fa {
                .id, .artefact_type, .status, .deadline,
                .storyboard_notes, .published_url, .editor_notes,
                .created_at, .updated_at,
                assigned_to_name: assignee.name,
                assigned_to_email: assignee.email,
                editor_name: editor.name,
                editor_email: editor.email,
                session_id: ss.id,
                arc_name: a.name
            } AS assignment
        """
        records = await self._read(query, {"id": assignment_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def update_assignment(
        self, assignment_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        set_clauses: list[str] = ["fa.updated_at = datetime()"]
        params: dict[str, object] = {"id": assignment_id}

        for field in ("status", "storyboard_notes", "published_url", "editor_notes"):
            if field in data and data[field] is not None:
                set_clauses.append(f"fa.{field} = ${field}")
                params[field] = data[field]

        query = f"""
            MATCH (fa:ForgeAssignment {{id: $id}})
            OPTIONAL MATCH (fa)-[:ASSIGNED_TO]->(assignee:Person)
            OPTIONAL MATCH (fa)-[:EDITED_BY]->(editor:Person)
            OPTIONAL MATCH (fa)-[:FOR_ARC]->(a:Arc)
            OPTIONAL MATCH (fa)-[:FOR_SESSION]->(ss:ScheduledSession)
            SET {', '.join(set_clauses)}
            RETURN fa {{
                .id, .artefact_type, .status, .deadline,
                .storyboard_notes, .published_url, .editor_notes,
                .created_at, .updated_at,
                assigned_to_name: assignee.name,
                assigned_to_email: assignee.email,
                editor_name: editor.name,
                editor_email: editor.email,
                session_id: ss.id,
                arc_name: a.name
            }} AS assignment
        """
        records = await self._write_and_return(query, params)
        if not records:
            return None
        return serialise_record(dict(records[0]["assignment"]))

    async def get_tracker(self, cycle_id: str) -> dict[str, object]:
        query = """
            MATCH (fa:ForgeAssignment)-[:FOR_SESSION]->(ss:ScheduledSession)-[:PART_OF]->(c:Cycle {id: $cycle_id})
            WITH fa, c
            WITH c,
                 count(CASE WHEN fa.status = 'published' THEN 1 END) AS produced,
                 fa.artefact_type AS artefact_type,
                 count(CASE WHEN fa.status = 'published' THEN 1 END) AS type_count
            WITH c.id AS cycle_id, sum(produced) AS total_produced,
                 collect({type: artefact_type, count: type_count}) AS type_breakdown
            RETURN cycle_id, total_produced,
                   apoc.map.fromPairs([t IN type_breakdown | [t.type, t.count]]) AS by_type
        """
        records = await self._read(query, {"cycle_id": cycle_id})
        if not records:
            return {"cycle_id": cycle_id, "produced": 0, "by_type": {}}
        record = records[0]
        return {
            "cycle_id": record["cycle_id"],
            "produced": record["total_produced"],
            "by_type": record.get("by_type", {}),
        }
