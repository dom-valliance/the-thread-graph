from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class ArcRepository(BaseRepository):
    async def list_arcs(self) -> list[dict[str, object]]:
        """List all themes (arcs) with bookmark and session counts."""
        query = """
            MATCH (th:Theme)
            OPTIONAL MATCH (th)<-[:HAS_THEME]-(b:Bookmark)
            WITH th, count(DISTINCT b) AS bookmark_count
            OPTIONAL MATCH (th)<-[:HAS_THEME]-(s:Session)
            WITH th, bookmark_count, count(DISTINCT s) AS session_count
            RETURN th {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count,
                session_count: session_count
            } AS arc
            ORDER BY arc.name
        """
        records = await self._read(query)
        return [serialise_record(dict(record["arc"])) for record in records]

    async def get_arc(self, name: str) -> dict[str, object] | None:
        """Get a single theme (arc) by name."""
        query = """
            MATCH (th:Theme {name: $name})
            OPTIONAL MATCH (th)<-[:HAS_THEME]-(b:Bookmark)
            WITH th, count(DISTINCT b) AS bookmark_count
            OPTIONAL MATCH (th)<-[:HAS_THEME]-(s:Session)
            WITH th, bookmark_count, count(DISTINCT s) AS session_count
            RETURN th {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count,
                session_count: session_count
            } AS arc
        """
        records = await self._read(query, {"name": name})
        if not records:
            return None
        return serialise_record(dict(records[0]["arc"]))

    async def get_arc_bookmarks(self, name: str) -> list[dict[str, object]]:
        """Get all bookmarks linked to a specific theme (arc)."""
        query = """
            MATCH (b:Bookmark)-[:HAS_THEME]->(th:Theme {name: $name})
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, collect(DISTINCT t.name) AS topic_names
            RETURN b {
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .date_added, .created_at, .updated_at,
                topic_names: topic_names
            } AS bookmark
            ORDER BY bookmark.date_added DESC
        """
        records = await self._read(query, {"name": name})
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def get_bridges(self) -> list[dict[str, object]]:
        """Get theme co-occurrence edges derived from shared bookmarks.

        Two themes are linked when at least one bookmark belongs to both
        (via topics that span themes). Returns pairs with a shared count.
        """
        query = """
            MATCH (th1:Theme)<-[:HAS_THEME]-(b:Bookmark)-[:TAGGED_WITH]->(t:Topic)
                  <-[:TAGGED_WITH]-(b2:Bookmark)-[:HAS_THEME]->(th2:Theme)
            WHERE th1.name < th2.name AND th1 <> th2
            WITH th1.name AS source, th2.name AS target, count(DISTINCT t) AS shared_topics
            RETURN source AS source_theme_name,
                   target AS target_theme_name,
                   shared_topics
            ORDER BY shared_topics DESC
        """
        records = await self._read(query)
        return [serialise_record(dict(record)) for record in records]
