from __future__ import annotations

import os

import httpx

from models.extraction import ExtractionContext
from models.session import SessionInput


class ApiClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or os.environ["API_BASE_URL"]).rstrip("/")
        self._http = httpx.AsyncClient(
            base_url=f"{self._base_url}/api/v1",
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._http.aclose()

    async def get_unprocessed_sessions(self) -> list[SessionInput]:
        response = await self._http.get("/sessions", params={"enriched": "false"})
        response.raise_for_status()
        data = response.json().get("data", [])
        return [SessionInput.model_validate(item) for item in data]

    async def get_extraction_context(self, session_id: str) -> ExtractionContext:
        response = await self._http.get(f"/sessions/{session_id}/extraction-context")
        response.raise_for_status()
        data = response.json().get("data", {})
        return ExtractionContext.model_validate(data)

    async def submit_arguments(self, arguments: list[dict[str, object]]) -> None:
        response = await self._http.post("/enrichment/arguments", json=arguments)
        response.raise_for_status()

    async def submit_action_items(self, items: list[dict[str, object]]) -> None:
        response = await self._http.post("/enrichment/action-items", json=items)
        response.raise_for_status()

    async def submit_evidence(self, evidence: list[dict[str, object]]) -> None:
        response = await self._http.post("/enrichment/evidence", json=evidence)
        response.raise_for_status()

    async def mark_session_enriched(self, session_id: str) -> None:
        response = await self._http.patch(
            f"/sessions/{session_id}", json={"enriched": True}
        )
        response.raise_for_status()
