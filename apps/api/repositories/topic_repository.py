from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class TopicRepository(BaseRepository):
    async def list_topics(self) -> list[dict[str, object]]:
        """List all topics with bookmark count, primary arc, and primary theme."""
        query = """
            MATCH (t:Topic)
            OPTIONAL MATCH (t)<-[:TAGGED_WITH]-(b:Bookmark)
            WITH t, count(b) AS bookmark_count
            OPTIONAL MATCH (t)<-[:TAGGED_WITH]-(b2:Bookmark)-[:BELONGS_TO_ARC]->(a:Arc)
            WITH t, bookmark_count, a.name AS arc, count(b2) AS arc_weight
            ORDER BY arc_weight DESC
            WITH t, bookmark_count, collect(arc)[0] AS primary_arc
            RETURN t {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count,
                primary_arc: primary_arc
            } AS topic
            ORDER BY topic.bookmark_count DESC, topic.name
        """
        records = await self._read(query)
        return [serialise_record(dict(record["topic"])) for record in records]

    async def get_topic_bookmarks(
        self, topic_name: str
    ) -> list[dict[str, object]]:
        """Get all bookmarks tagged with a specific topic."""
        query = """
            MATCH (b:Bookmark)-[:TAGGED_WITH]->(t:Topic {name: $topic_name})
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t2:Topic)
            WITH b, collect(DISTINCT t2.name) AS topic_names
            OPTIONAL MATCH (b)-[:HAS_THEME]->(th:Theme)
            RETURN b {
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .time_consumption, .date_added, .created_at, .updated_at,
                topic_names: topic_names,
                theme_name: th.name
            } AS bookmark
            ORDER BY bookmark.date_added DESC
        """
        records = await self._read(query, {"topic_name": topic_name})
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def get_cross_arc_topics(self) -> list[dict[str, object]]:
        """Get topics appearing in bookmarks across 3+ themes."""
        query = """
            MATCH (t:Topic)<-[:TAGGED_WITH]-(b:Bookmark)-[:HAS_THEME]->(th:Theme)
            WITH t, collect(DISTINCT th.name) AS theme_names
            WHERE size(theme_names) >= 3
            OPTIONAL MATCH (t)<-[:TAGGED_WITH]-(b2:Bookmark)
            WITH t, theme_names, count(DISTINCT b2) AS bookmark_count
            RETURN t {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count,
                theme_count: size(theme_names)
            } AS topic
            ORDER BY topic.theme_count DESC, topic.name
        """
        records = await self._read(query)
        return [serialise_record(dict(record["topic"])) for record in records]

    async def get_co_occurrences(self) -> list[dict[str, object]]:
        """Get topic pairs that appear on the same bookmark."""
        query = """
            MATCH (t1:Topic)<-[:TAGGED_WITH]-(b:Bookmark)-[:TAGGED_WITH]->(t2:Topic)
            WHERE t1.name < t2.name
            WITH t1.name AS name, t2.name AS co_occurring_topic, count(b) AS count
            RETURN name, co_occurring_topic, count
            ORDER BY count DESC
        """
        records = await self._read(query)
        return [serialise_record(dict(record)) for record in records]
