from __future__ import annotations

from core.exceptions import NotFoundError
from models.session import (
    ActionItemSummary,
    ArgumentSummary,
    ReferencedBookmark,
    SessionDetail,
    SessionResponse,
)
from repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository) -> None:
        self._repo = repository

    async def list_sessions(
        self,
        arc: str | None = None,
        person: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        cursor: str | None = None,
        limit: int = 25,
    ) -> list[SessionResponse]:
        rows = await self._repo.list_sessions(
            arc=arc,
            person=person,
            date_from=date_from,
            date_to=date_to,
            cursor=cursor,
            limit=limit,
        )
        return [SessionResponse(**row) for row in rows]

    async def get_session_detail(self, notion_id: str) -> SessionDetail:
        row = await self._repo.get_session(notion_id)
        if row is None:
            raise NotFoundError(f"Session '{notion_id}' not found")

        # Filter out empty relationship entries produced by OPTIONAL MATCH
        arguments = [
            ArgumentSummary(**a)
            for a in row.pop("arguments", [])
            if a.get("id") is not None
        ]
        action_items = [
            ActionItemSummary(**ai)
            for ai in row.pop("action_items", [])
            if ai.get("id") is not None
        ]
        bookmarks = [
            ReferencedBookmark(**b)
            for b in row.pop("referenced_bookmarks", [])
            if b.get("notion_id") is not None
        ]

        return SessionDetail(
            **row,
            arguments=arguments,
            action_items=action_items,
            referenced_bookmarks=bookmarks,
        )

    async def upsert_sessions(self, sessions: list[dict[str, object]]) -> int:
        return await self._repo.upsert_sessions(sessions)
