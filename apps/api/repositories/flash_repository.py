from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class FlashRepository(BaseRepository):
    async def create_flash(self, data: dict[str, object]) -> dict[str, object] | None:
        query = """
            CREATE (f:Flash {
                id: $id,
                title: $title,
                description: $description,
                status: 'pending',
                reviewed_date: null,
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH f
            MATCH (p:Position {id: $position_id})
            CREATE (f)-[:AFFECTS]->(p)
            WITH f, p
            MATCH (person:Person {email: $raised_by_email})
            CREATE (f)-[:RAISED_BY]->(person)
            RETURN f {
                .id, .title, .description, .status,
                .reviewed_date, .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                raised_by_name: person.name,
                raised_by_email: person.email
            } AS flash
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        return serialise_record(dict(records[0]["flash"]))

    async def list_flashes(
        self,
        status: str | None = None,
        position_id: str | None = None,
    ) -> list[dict[str, object]]:
        where_clauses: list[str] = []
        params: dict[str, object] = {}

        if status is not None:
            where_clauses.append("f.status = $status")
            params["status"] = status

        if position_id is not None:
            where_clauses.append("p.id = $position_id")
            params["position_id"] = position_id

        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        query = f"""
            MATCH (f:Flash)-[:AFFECTS]->(p:Position)
            OPTIONAL MATCH (f)-[:RAISED_BY]->(person:Person)
            {where}
            RETURN f {{
                .id, .title, .description, .status,
                .reviewed_date, .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                raised_by_name: person.name,
                raised_by_email: person.email
            }} AS flash
            ORDER BY f.created_at DESC
        """
        records = await self._read(query, params)
        return [serialise_record(dict(record["flash"])) for record in records]

    async def get_pending(self) -> list[dict[str, object]]:
        return await self.list_flashes(status="pending")

    async def update_flash(
        self, flash_id: str, data: dict[str, object]
    ) -> dict[str, object] | None:
        set_clauses: list[str] = ["f.updated_at = datetime()"]
        params: dict[str, object] = {"id": flash_id}

        if "status" in data and data["status"] is not None:
            set_clauses.append("f.status = $status")
            params["status"] = data["status"]

        if "reviewed_date" in data and data["reviewed_date"] is not None:
            set_clauses.append("f.reviewed_date = datetime($reviewed_date)")
            params["reviewed_date"] = data["reviewed_date"]

        query = f"""
            MATCH (f:Flash {{id: $id}})
            OPTIONAL MATCH (f)-[:AFFECTS]->(p:Position)
            OPTIONAL MATCH (f)-[:RAISED_BY]->(person:Person)
            SET {', '.join(set_clauses)}
            RETURN f {{
                .id, .title, .description, .status,
                .reviewed_date, .created_at, .updated_at,
                position_id: p.id,
                position_text: p.text,
                raised_by_name: person.name,
                raised_by_email: person.email
            }} AS flash
        """
        records = await self._write_and_return(query, params)
        if not records:
            return None
        return serialise_record(dict(records[0]["flash"]))
