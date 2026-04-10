from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class BridgeRepository(BaseRepository):
    async def get_cross_arc_bridges(self) -> list[dict[str, object]]:
        """Get all position-to-position bridges across arcs."""
        query = """
            MATCH (sp:Position)-[br:BRIDGES_TO]->(tp:Position)
            MATCH (sp)-[:LOCKED_IN]->(sa:Arc)
            MATCH (tp)-[:LOCKED_IN]->(ta:Arc)
            WHERE sa <> ta
            RETURN br {
                .strength, .label,
                source_position_id: sp.id,
                source_position_text: sp.text,
                source_arc_name: sa.name,
                source_arc_number: sa.number,
                target_position_id: tp.id,
                target_position_text: tp.text,
                target_arc_name: ta.name,
                target_arc_number: ta.number
            } AS bridge
            ORDER BY sa.number, ta.number
        """
        records = await self._read(query)
        return [serialise_record(dict(record["bridge"])) for record in records]

    async def get_unconnected_positions(self) -> list[dict[str, object]]:
        """Get locked positions with no cross-arc bridges."""
        query = """
            MATCH (p:Position {status: 'locked'})-[:LOCKED_IN]->(a:Arc)
            WHERE NOT EXISTS { (p)-[:BRIDGES_TO]->(:Position) }
              AND NOT EXISTS { (:Position)-[:BRIDGES_TO]->(p) }
            RETURN p {
                .id, .text,
                arc_name: a.name,
                arc_number: a.number
            } AS position
            ORDER BY a.number
        """
        records = await self._read(query)
        return [serialise_record(dict(record["position"])) for record in records]
