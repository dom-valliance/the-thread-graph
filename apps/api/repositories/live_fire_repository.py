from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class LiveFireRepository(BaseRepository):
    async def create_entry(self, data: dict[str, object]) -> dict[str, object] | None:
        query = """
            CREATE (lf:LiveFireEntry {
                id: $id,
                outcome: $outcome,
                context: $context,
                date: date($date),
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH lf
            MATCH (p:Position {id: $position_id})
            CREATE (lf)-[:REFERENCES]->(p)
            WITH lf, p
            OPTIONAL MATCH (orp:ObjectionResponsePair {id: $objection_pair_id})
            FOREACH (_ IN CASE WHEN orp IS NOT NULL THEN [1] ELSE [] END |
                CREATE (lf)-[:REFERENCES]->(orp)
            )
            WITH lf, p
            MATCH (person:Person {email: $reporter_email})
            CREATE (lf)-[:REPORTED_BY]->(person)
            WITH lf, p, person
            OPTIONAL MATCH (ss:ScheduledSession {id: $session_id})
            FOREACH (_ IN CASE WHEN ss IS NOT NULL THEN [1] ELSE [] END |
                CREATE (lf)-[:REPORTED_IN]->(ss)
            )
            RETURN lf {
                .id, .outcome, .context, .date,
                .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                reporter_name: person.name,
                reporter_email: person.email
            } AS entry
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["entry"]))

    async def list_entries(
        self,
        position_id: str | None = None,
        outcome: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, object]]:
        where_clauses: list[str] = []
        params: dict[str, object] = {}

        if position_id is not None:
            where_clauses.append("p.id = $position_id")
            params["position_id"] = position_id

        if outcome is not None:
            where_clauses.append("lf.outcome = $outcome")
            params["outcome"] = outcome

        if date_from is not None:
            where_clauses.append("lf.date >= date($date_from)")
            params["date_from"] = date_from

        if date_to is not None:
            where_clauses.append("lf.date <= date($date_to)")
            params["date_to"] = date_to

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            MATCH (lf:LiveFireEntry)-[:REFERENCES]->(p:Position)
            OPTIONAL MATCH (lf)-[:REPORTED_BY]->(person:Person)
            {where}
            RETURN lf {{
                .id, .outcome, .context, .date,
                .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                reporter_name: person.name,
                reporter_email: person.email
            }} AS entry
            ORDER BY lf.date DESC
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["entry"])) for record in records]

    async def get_metrics(self) -> list[dict[str, object]]:
        query = """
            MATCH (p:Position {status: 'locked'})
            OPTIONAL MATCH (lf:LiveFireEntry)-[:REFERENCES]->(p)
            WITH p,
                count(lf) AS total_uses,
                count(CASE WHEN lf.outcome = 'used_successfully' THEN 1 END) AS successes,
                count(CASE WHEN lf.outcome = 'used_and_failed' THEN 1 END) AS failures,
                max(lf.date) AS last_used
            RETURN p.id AS position_id,
                   p.text AS position_text,
                   total_uses,
                   successes,
                   failures,
                   CASE WHEN total_uses > 0
                       THEN toFloat(successes) / total_uses
                       ELSE null
                   END AS success_rate,
                   last_used,
                   total_uses = 0 AS never_used
            ORDER BY position_id
        """
        records = await self._read(query)
        return [serialise_record(dict(record)) for record in records]
