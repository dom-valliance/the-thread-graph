from __future__ import annotations

from pydantic import BaseModel


class ArcResponse(BaseModel):
    name: str
    bookmark_count: int = 0
    session_count: int = 0
    created_at: str
    updated_at: str


class ArcBridgeResponse(BaseModel):
    source_arc_name: str
    target_arc_name: str
    shared_topics: int


class BookmarkEdge(BaseModel):
    source_notion_id: str
    target_notion_id: str
    shared_topics: int
    shared_topic_names: list[str] = []


class BookmarkEdgeRequest(BaseModel):
    notion_ids: list[str]


class ArcDetail(BaseModel):
    name: str
    bookmark_count: int = 0
    session_count: int = 0
    bookmarks: list[dict] = []
    created_at: str
    updated_at: str
