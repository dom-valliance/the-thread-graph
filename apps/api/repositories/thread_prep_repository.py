from __future__ import annotations

import json

from repositories.base import BaseRepository, serialise_record


class ThreadPrepRepository(BaseRepository):
    async def get_brief_for_session(
        self, session_id: str
    ) -> dict[str, object] | None:
        query = """
            MATCH (tpb:ThreadPrepBrief)-[:FOR_SESSION]->(ss:ScheduledSession {id: $session_id})
            OPTIONAL MATCH (tpb)-[:FOR_ARC]->(a:Arc)
            RETURN tpb {
                .id, .week_type, .arc_number, .arc_name,
                .sharpened_problem_question, .problem_question_rationale,
                .sharpened_landscape_question, .landscape_question_rationale,
                .steelman_argument, .steelman_rationale,
                .workshop_grid_criteria_json,
                .new_evidence_since_week1, .objection_fuel,
                .cross_arc_bridge_prompts, .p1_v1_signal,
                .bookmark_anchor_mapping_json, .reading_assignments_json,
                .adjacent_bookmarks_json, .flash_checks_json,
                .bookmark_count, .raw_markdown,
                .status, .created_at, .updated_at,
                session_id: $session_id
            } AS brief
        """
        records = await self._read(query, {"session_id": session_id})
        if not records:
            return None
        row = serialise_record(dict(records[0]["brief"]))
        return _deserialise_json_fields(row)

    async def create_brief(self, data: dict[str, object]) -> dict[str, object] | None:
        query = """
            CREATE (tpb:ThreadPrepBrief {
                id: $id,
                week_type: $week_type,
                arc_number: $arc_number,
                arc_name: $arc_name,
                sharpened_problem_question: $sharpened_problem_question,
                problem_question_rationale: $problem_question_rationale,
                sharpened_landscape_question: $sharpened_landscape_question,
                landscape_question_rationale: $landscape_question_rationale,
                steelman_argument: $steelman_argument,
                steelman_rationale: $steelman_rationale,
                workshop_grid_criteria_json: $workshop_grid_criteria_json,
                new_evidence_since_week1: $new_evidence_since_week1,
                objection_fuel: $objection_fuel,
                cross_arc_bridge_prompts: $cross_arc_bridge_prompts,
                p1_v1_signal: $p1_v1_signal,
                bookmark_anchor_mapping_json: $bookmark_anchor_mapping_json,
                reading_assignments_json: $reading_assignments_json,
                adjacent_bookmarks_json: $adjacent_bookmarks_json,
                flash_checks_json: $flash_checks_json,
                bookmark_count: $bookmark_count,
                raw_markdown: $raw_markdown,
                status: $status,
                created_at: datetime(),
                updated_at: datetime()
            })
            WITH tpb
            MATCH (ss:ScheduledSession {id: $session_id})
            CREATE (tpb)-[:FOR_SESSION]->(ss)
            WITH tpb
            OPTIONAL MATCH (a:Arc {number: $arc_number})
            FOREACH (_ IN CASE WHEN a IS NOT NULL THEN [1] ELSE [] END |
                CREATE (tpb)-[:FOR_ARC]->(a)
            )
            WITH tpb
            FOREACH (bk_nid IN $bookmark_notion_ids |
                MERGE (b:Bookmark {notion_id: bk_nid})
                CREATE (tpb)-[:USES_BOOKMARK]->(b)
            )
            RETURN tpb {
                .id, .week_type, .arc_number, .arc_name,
                .sharpened_problem_question, .problem_question_rationale,
                .sharpened_landscape_question, .landscape_question_rationale,
                .steelman_argument, .steelman_rationale,
                .workshop_grid_criteria_json,
                .new_evidence_since_week1, .objection_fuel,
                .cross_arc_bridge_prompts, .p1_v1_signal,
                .bookmark_anchor_mapping_json, .reading_assignments_json,
                .adjacent_bookmarks_json, .flash_checks_json,
                .bookmark_count, .raw_markdown,
                .status, .created_at, .updated_at,
                session_id: $session_id
            } AS brief
        """
        records = await self._write_and_return(query, data)
        if not records:
            return None
        row = serialise_record(dict(records[0]["brief"]))
        return _deserialise_json_fields(row)

    async def delete_brief_for_session(self, session_id: str) -> bool:
        query = """
            MATCH (tpb:ThreadPrepBrief)-[:FOR_SESSION]->(ss:ScheduledSession {id: $session_id})
            DETACH DELETE tpb
        """
        summary = await self._write(query, {"session_id": session_id})
        return summary.counters.nodes_deleted > 0

    async def get_bookmarks_for_prep(
        self, arc_number: int, days_back: int = 14
    ) -> list[dict[str, object]]:
        """Get recent bookmarks for an arc with rich data for LLM prompting."""
        query = """
            MATCH (b:Bookmark)-[:BELONGS_TO_ARC]->(a:Arc {number: $arc_number})
            WHERE b.date_added IS NOT NULL
              AND b.date_added >= date() - duration({days: $days_back})
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, collect(DISTINCT t.name) AS topic_names
            OPTIONAL MATCH (b)-[:BELONGS_TO_ARC]->(other_arc:Arc)
            WHERE other_arc.number <> $arc_number
            WITH b, topic_names, collect(DISTINCT other_arc.name) AS other_arc_names
            RETURN b {
                .notion_id, .title, .url, .source,
                .ai_summary, .valliance_viewpoint,
                .edge_or_foundational, .focus,
                .date_added,
                topic_names: topic_names,
                other_arc_names: other_arc_names
            } AS bookmark
            ORDER BY b.date_added DESC
        """
        records = await self._read(
            query, {"arc_number": arc_number, "days_back": days_back}
        )
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def get_locked_positions_for_arc(
        self, arc_number: int
    ) -> list[dict[str, object]]:
        """Get locked positions for an arc (for Flash checks and Week 2 context)."""
        query = """
            MATCH (p:Position {status: 'locked'})-[:LOCKED_IN]->(a:Arc {number: $arc_number})
            RETURN p {
                .id, .text, .anti_position_text,
                .cross_arc_bridge_text, .p1_v1_mapping,
                .locked_date
            } AS position
            ORDER BY p.locked_date DESC
        """
        records = await self._read(query, {"arc_number": arc_number})
        return [serialise_record(dict(record["position"])) for record in records]

    async def get_all_locked_positions(self) -> list[dict[str, object]]:
        """Get all locked positions across arcs (for Flash checks)."""
        query = """
            MATCH (p:Position {status: 'locked'})-[:LOCKED_IN]->(a:Arc)
            RETURN p {
                .id, .text, .locked_date
            } AS position, a.number AS arc_number, a.name AS arc_name
            ORDER BY a.number
        """
        records = await self._read(query)
        results = []
        for record in records:
            pos = serialise_record(dict(record["position"]))
            pos["arc_number"] = record["arc_number"]
            pos["arc_name"] = record["arc_name"]
            results.append(pos)
        return results


def _deserialise_json_fields(row: dict[str, object]) -> dict[str, object]:
    """Parse JSON string fields back into lists for the response model."""
    json_mappings = {
        "workshop_grid_criteria_json": "workshop_grid_criteria",
        "bookmark_anchor_mapping_json": "bookmark_anchor_mapping",
        "reading_assignments_json": "reading_assignments",
        "adjacent_bookmarks_json": "adjacent_bookmarks",
        "flash_checks_json": "flash_checks",
    }
    for json_key, target_key in json_mappings.items():
        raw = row.pop(json_key, None)
        if raw and isinstance(raw, str):
            try:
                row[target_key] = json.loads(raw)
            except json.JSONDecodeError:
                row[target_key] = []
        else:
            row[target_key] = raw if isinstance(raw, list) else []
    return row
