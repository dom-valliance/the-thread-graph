from __future__ import annotations

from repositories.base import BaseRepository, serialise_record


class ArcRepository(BaseRepository):
    async def list_arcs(self) -> list[dict[str, object]]:
        """List all arcs with bookmark and session counts."""
        query = """
            MATCH (a:Arc)
            OPTIONAL MATCH (a)<-[:BELONGS_TO_ARC]-(b:Bookmark)
            WITH a, count(DISTINCT b) AS bookmark_count
            OPTIONAL MATCH (a)<-[:COVERS]-(s:Session)
            WITH a, bookmark_count, count(DISTINCT s) AS session_count
            RETURN a {
                .name, .created_at, .updated_at,
                bookmark_count: bookmark_count,
                session_count: session_count
            } AS arc
            ORDER BY arc.name
        """
        records = await self._read(query)
        return [serialise_record(dict(record["arc"])) for record in records]

    async def get_arc(self, name: str) -> dict[str, object] | None:
        """Get a single arc by name."""
        query = """
            MATCH (a:Arc {name: $name})
            OPTIONAL MATCH (a)<-[:BELONGS_TO_ARC]-(b:Bookmark)
            WITH a, count(DISTINCT b) AS bookmark_count
            OPTIONAL MATCH (a)<-[:COVERS]-(s:Session)
            WITH a, bookmark_count, count(DISTINCT s) AS session_count
            RETURN a {
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
        """Get all bookmarks linked to a specific arc."""
        query = """
            MATCH (b:Bookmark)-[:BELONGS_TO_ARC]->(a:Arc {name: $name})
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

    async def get_arc_bookmarks_paginated(
        self, name: str, offset: int = 0, limit: int = 10
    ) -> list[dict[str, object]]:
        """Get paginated bookmarks for an arc, ordered by date_added DESC."""
        query = """
            MATCH (b:Bookmark)-[:BELONGS_TO_ARC]->(a:Arc {name: $name})
            OPTIONAL MATCH (b)-[:TAGGED_WITH]->(t:Topic)
            WITH b, collect(DISTINCT t.name) AS topic_names
            OPTIONAL MATCH (b)-[:BELONGS_TO_ARC]->(arc:Arc)
            WITH b, topic_names, collect(DISTINCT arc.name) AS arc_bucket_names
            RETURN b {
                .notion_id, .title, .source, .url, .ai_summary,
                .valliance_viewpoint, .edge_or_foundational, .focus,
                .date_added, .created_at, .updated_at,
                topic_names: topic_names,
                arc_bucket_names: arc_bucket_names
            } AS bookmark
            ORDER BY bookmark.date_added DESC, bookmark.notion_id DESC
            SKIP $offset
            LIMIT $limit
        """
        records = await self._read(
            query, {"name": name, "offset": offset, "limit": limit}
        )
        return [serialise_record(dict(record["bookmark"])) for record in records]

    async def get_bookmark_edges(
        self, notion_ids: list[str]
    ) -> list[dict[str, object]]:
        """Get bookmark-to-bookmark edges based on shared topics.

        Only computes edges between the provided set of notion_ids.
        """
        if len(notion_ids) < 2:
            return []

        query = """
            MATCH (b1:Bookmark)-[:TAGGED_WITH]->(t:Topic)<-[:TAGGED_WITH]-(b2:Bookmark)
            WHERE b1.notion_id IN $notion_ids
              AND b2.notion_id IN $notion_ids
              AND b1.notion_id < b2.notion_id
            WITH b1.notion_id AS source, b2.notion_id AS target,
                 collect(DISTINCT t.name) AS shared_topic_names
            RETURN source AS source_notion_id,
                   target AS target_notion_id,
                   size(shared_topic_names) AS shared_topics,
                   shared_topic_names
            ORDER BY shared_topics DESC
        """
        records = await self._read(query, {"notion_ids": notion_ids})
        return [serialise_record(dict(record)) for record in records]

    async def get_bridges(self) -> list[dict[str, object]]:
        """Get arc co-occurrence edges derived from shared topics.

        Two arcs are linked when their bookmarks share at least one topic.
        Returns pairs with a shared topic count.
        """
        query = """
            MATCH (a1:Arc)<-[:BELONGS_TO_ARC]-(b:Bookmark)-[:TAGGED_WITH]->(t:Topic)
                  <-[:TAGGED_WITH]-(b2:Bookmark)-[:BELONGS_TO_ARC]->(a2:Arc)
            WHERE a1.name < a2.name AND a1 <> a2
            WITH a1.name AS source, a2.name AS target, count(DISTINCT t) AS shared_topics
            RETURN source AS source_arc_name,
                   target AS target_arc_name,
                   shared_topics
            ORDER BY shared_topics DESC
        """
        records = await self._read(query)
        return [serialise_record(dict(record)) for record in records]
