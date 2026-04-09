from __future__ import annotations

from core.exceptions import NotFoundError
from models.bookmark import BookmarkResponse
from models.topic import TopicCoOccurrence, TopicResponse
from repositories.topic_repository import TopicRepository


class TopicService:
    def __init__(self, repository: TopicRepository) -> None:
        self._repo = repository

    async def list_topics(self) -> list[TopicResponse]:
        rows = await self._repo.list_topics()
        return [TopicResponse(**row) for row in rows]

    async def get_topic_bookmarks(self, topic_name: str) -> list[BookmarkResponse]:
        rows = await self._repo.get_topic_bookmarks(topic_name)
        if not rows:
            # Verify the topic exists before returning empty
            all_topics = await self._repo.list_topics()
            topic_names = [t["name"] for t in all_topics]
            if topic_name not in topic_names:
                raise NotFoundError(f"Topic '{topic_name}' not found")
        return [BookmarkResponse(**row) for row in rows]

    async def get_cross_arc_topics(self) -> list[TopicResponse]:
        rows = await self._repo.get_cross_arc_topics()
        return [TopicResponse(**row) for row in rows]

    async def get_co_occurrences(self) -> list[TopicCoOccurrence]:
        rows = await self._repo.get_co_occurrences()
        return [TopicCoOccurrence(**row) for row in rows]
