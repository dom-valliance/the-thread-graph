from __future__ import annotations

from repositories.base import BaseRepository

# Maps entity types to their full-text index name, primary key field,
# title field, and snippet field.
_INDEX_CONFIG: dict[str, dict[str, str]] = {
    "bookmark": {
        "index": "bookmark_search",
        "id_field": "id",
        "title_field": "title",
        "snippet_field": "ai_summary",
    },
    "position": {
        "index": "position_search",
        "id_field": "id",
        "title_field": "text",
        "snippet_field": "text",
    },
    "argument": {
        "index": "argument_search",
        "id_field": "id",
        "title_field": "text",
        "snippet_field": "text",
    },
}


class SearchRepository(BaseRepository):
    async def search(
        self,
        query_text: str,
        entity_types: list[str] | None = None,
    ) -> list[dict[str, object]]:
        """Run a full-text search across configured Neo4j indexes.

        Queries each applicable full-text index, unions results, and
        returns them sorted by descending score.
        """
        applicable = (
            {et: _INDEX_CONFIG[et] for et in entity_types if et in _INDEX_CONFIG}
            if entity_types
            else _INDEX_CONFIG
        )

        results: list[dict[str, object]] = []
        for entity_type, config in applicable.items():
            query = """
                CALL db.index.fulltext.queryNodes($index, $query_text)
                YIELD node, score
                RETURN
                    $entity_type AS entity_type,
                    node[$id_field] AS id,
                    node[$title_field] AS title,
                    node[$snippet_field] AS snippet,
                    score
                ORDER BY score DESC
                LIMIT 20
            """
            params: dict[str, object] = {
                "index": config["index"],
                "query_text": query_text,
                "entity_type": entity_type,
                "id_field": config["id_field"],
                "title_field": config["title_field"],
                "snippet_field": config["snippet_field"],
            }
            records = await self._read(query, params)
            results.extend(
                {
                    "entity_type": record["entity_type"],
                    "id": record["id"],
                    "title": record["title"],
                    "snippet": record["snippet"] or "",
                    "score": record["score"],
                }
                for record in records
            )

        # Sort combined results by score descending.
        results.sort(key=lambda r: r["score"], reverse=True)  # type: ignore[arg-type]
        return results
