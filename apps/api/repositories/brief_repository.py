from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class BriefRepository(BaseRepository):
    async def create_brief(self, data: dict[str, object]) -> dict[str, object] | None:
        query = """
            CREATE (b:ProblemLandscapeBrief {
                id: $id,
                problem_statement: $problem_statement,
                landscape_criteria: $landscape_criteria,
                steelman_summary: $steelman_summary,
                status: 'draft',
                locked_date: null,
                locked_by: null,
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH b
            OPTIONAL MATCH (ss:ScheduledSession {id: $session_id})
            FOREACH (_ IN CASE WHEN ss IS NOT NULL THEN [1] ELSE [] END |
                CREATE (b)-[:PRODUCED_IN]->(ss)
            )
            WITH b
            OPTIONAL MATCH (a:Arc {name: $arc_name})
            FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
                CREATE (b)-[:FOR_ARC]->(a)
            )
            RETURN b {
                .id, .problem_statement, .landscape_criteria,
                .steelman_summary, .status, .locked_date, .locked_by,
                .created_at, .updated_at,
                session_id: $session_id,
                arc_name: $arc_name
            } AS brief
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["brief"]))

    async def get_brief(self, brief_id: str) -> dict[str, object] | None:
        query = """
            MATCH (b:ProblemLandscapeBrief {id: $id})
            OPTIONAL MATCH (b)-[:PRODUCED_IN]->(ss:ScheduledSession)
            OPTIONAL MATCH (b)-[:FOR_ARC]->(a:Arc)
            OPTIONAL MATCH (lg:LandscapeGrid)-[:PART_OF]->(b)
            OPTIONAL MATCH (lge:LandscapeGridEntry)-[:ENTRY_IN]->(lg)
            WITH b, ss, a, lg,
                 collect(CASE WHEN lge IS NOT NULL THEN lge {
                     .id, .player_name, .criterion, .rating, .notes
                 } ELSE null END) AS entries
            RETURN b {
                .id, .problem_statement, .landscape_criteria,
                .steelman_summary, .status, .locked_date, .locked_by,
                .created_at, .updated_at,
                session_id: ss.id,
                arc_name: a.name,
                landscape_grid: CASE WHEN lg IS NOT NULL THEN {
                    id: lg.id,
                    entries: [e IN entries WHERE e IS NOT NULL]
                } ELSE null END
            } AS brief
        """
        records = await self._read(query, {"id": brief_id})
        if not records:
            return None
        return serialise_record(dict(records[0]["brief"]))

    async def update_brief(
        self, brief_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        set_clauses: list[str] = []
        params: dict[str, object] = {"id": brief_id}

        for field in ("problem_statement", "landscape_criteria", "steelman_summary"):
            if field in data and data[field] is not None:
                set_clauses.append(f"b.{field} = ${field}")
                params[field] = data[field]

        if not set_clauses:
            return await self.get_brief(brief_id)

        set_clauses.append("b.updated_at = datetime()")

        query = f"""
            MATCH (b:ProblemLandscapeBrief {{id: $id}})
            WHERE b.status = 'draft'
            SET {', '.join(set_clauses)}
            RETURN b {{
                .id, .problem_statement, .landscape_criteria,
                .steelman_summary, .status, .locked_date, .locked_by,
                .created_at, .updated_at
            }} AS brief
        """
        records = await self._write_and_return(query, params)
        if not records:
            return None
        return serialise_record(dict(records[0]["brief"]))

    async def get_brief_status(self, brief_id: str) -> str | None:
        query = """
            MATCH (b:ProblemLandscapeBrief {id: $id})
            RETURN b.status AS status
        """
        records = await self._read(query, {"id": brief_id})
        if not records:
            return None
        return records[0]["status"]

    async def lock_brief(
        self, brief_id: str, locked_by: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (b:ProblemLandscapeBrief {id: $id})
            WHERE b.status = 'draft'
            SET b.status = 'locked',
                b.locked_date = datetime(),
                b.locked_by = $locked_by,
                b.updated_at = datetime()
            RETURN b {
                .id, .problem_statement, .landscape_criteria,
                .steelman_summary, .status, .locked_date, .locked_by,
                .created_at, .updated_at
            } AS brief
        """
        records = await self._write_and_return(
            query, {"id": brief_id, "locked_by": locked_by}
        )
        if not records:
            return None
        return serialise_record(dict(records[0]["brief"]))

    async def add_grid_entries(
        self, brief_id: str, grid_id: str, entries: list[dict[str, object]]
    ) -> dict[str, object] | None:
        query = """
            MATCH (b:ProblemLandscapeBrief {id: $brief_id})
            MERGE (lg:LandscapeGrid {id: $grid_id})
            ON CREATE SET lg.created_at = datetime(), lg.updated_at = datetime()
            ON MATCH SET lg.updated_at = datetime()
            MERGE (lg)-[:PART_OF]->(b)
            WITH lg
            UNWIND $entries AS entry
            CREATE (lge:LandscapeGridEntry {
                id: entry.id,
                player_name: entry.player_name,
                criterion: entry.criterion,
                rating: entry.rating,
                notes: entry.notes
            })
            CREATE (lge)-[:ENTRY_IN]->(lg)
            WITH lge, entry
            MERGE (pl:Player {name: entry.player_name})
            ON CREATE SET pl.created_at = datetime(), pl.updated_at = datetime()
            MERGE (lge)-[:EVALUATES]->(pl)
            RETURN count(lge) AS count
        """
        records = await self._write_and_return(query, {
            "brief_id": brief_id,
            "grid_id": grid_id,
            "entries": entries,
        })
        if not records:
            return None
        return {"count": records[0]["count"]}
