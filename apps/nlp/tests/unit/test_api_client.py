from __future__ import annotations

import httpx
import pytest

from client.api_client import ApiClient
from models.extraction import ExtractionContext
from models.session import SessionInput


@pytest.fixture()
async def api_client(monkeypatch: pytest.MonkeyPatch) -> ApiClient:
    monkeypatch.setenv("API_BASE_URL", "http://test-api:8000")
    client = ApiClient()
    yield client
    await client.close()


def _mock_response(json_data: dict | list, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        json=json_data,
        request=httpx.Request("GET", "http://test-api:8000"),
    )


class TestApiClient:
    async def test_get_unprocessed_sessions(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        response_data = {
            "data": [
                {
                    "notion_id": "s-1",
                    "title": "Session 1",
                    "transcript": "Some transcript",
                },
                {
                    "notion_id": "s-2",
                    "title": "Session 2",
                    "transcript": "Another transcript",
                },
            ]
        }

        async def mock_get(url, **kwargs):
            return _mock_response(response_data)

        monkeypatch.setattr(api_client._http, "get", mock_get)

        sessions = await api_client.get_unprocessed_sessions()

        assert len(sessions) == 2
        assert all(isinstance(s, SessionInput) for s in sessions)
        assert sessions[0].notion_id == "s-1"
        assert sessions[1].title == "Session 2"

    async def test_get_extraction_context(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        response_data = {
            "data": {
                "session_id": "s-1",
                "arc_name": "Agentic AI",
                "existing_topics": ["AI", "Consulting"],
            }
        }

        async def mock_get(url, **kwargs):
            return _mock_response(response_data)

        monkeypatch.setattr(api_client._http, "get", mock_get)

        context = await api_client.get_extraction_context("s-1")

        assert isinstance(context, ExtractionContext)
        assert context.session_id == "s-1"
        assert context.arc_name == "Agentic AI"
        assert context.existing_topics == ["AI", "Consulting"]

    async def test_submit_arguments(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[tuple[str, list]] = []

        async def mock_post(url, **kwargs):
            calls.append((url, kwargs.get("json")))
            return _mock_response({})

        monkeypatch.setattr(api_client._http, "post", mock_post)

        args = [{"id": "arg-1", "text": "Test"}]
        await api_client.submit_arguments(args)

        assert len(calls) == 1
        assert calls[0][0] == "/enrichment/arguments"
        assert calls[0][1] == args

    async def test_submit_action_items(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[tuple[str, list]] = []

        async def mock_post(url, **kwargs):
            calls.append((url, kwargs.get("json")))
            return _mock_response({})

        monkeypatch.setattr(api_client._http, "post", mock_post)

        items = [{"id": "ai-1", "text": "Do something"}]
        await api_client.submit_action_items(items)

        assert calls[0][0] == "/enrichment/action-items"

    async def test_submit_evidence(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[tuple[str, list]] = []

        async def mock_post(url, **kwargs):
            calls.append((url, kwargs.get("json")))
            return _mock_response({})

        monkeypatch.setattr(api_client._http, "post", mock_post)

        evidence = [{"id": "ev-1", "text": "Some data point", "type": "data_point"}]
        await api_client.submit_evidence(evidence)

        assert calls[0][0] == "/enrichment/evidence"

    async def test_mark_session_enriched(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[tuple[str, dict]] = []

        async def mock_patch(url, **kwargs):
            calls.append((url, kwargs.get("json")))
            return _mock_response({})

        monkeypatch.setattr(api_client._http, "patch", mock_patch)

        await api_client.mark_session_enriched("s-1")

        assert calls[0][0] == "/sessions/s-1"
        assert calls[0][1] == {"enriched": True}

    async def test_raises_on_http_error(
        self,
        api_client: ApiClient,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def mock_get(url, **kwargs):
            return _mock_response({"error": "not found"}, status_code=404)

        monkeypatch.setattr(api_client._http, "get", mock_get)

        with pytest.raises(httpx.HTTPStatusError):
            await api_client.get_unprocessed_sessions()
