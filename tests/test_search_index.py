from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.app.services import search_index


def test_documents_index_mapping_uses_russian_analyzer() -> None:
    mapping = search_index.INDEX_MAPPING

    assert "analysis-ru" in mapping["settings"]["analysis"]["analyzer"]
    assert mapping["mappings"]["properties"]["text"] == {
        "type": "text",
        "analyzer": "analysis-ru",
    }
    assert set(mapping["mappings"]["properties"]) == {
        "chunk_id",
        "file_name",
        "page_number",
        "text",
    }


@pytest.mark.anyio
async def test_search_documents_uses_multi_match_by_text_and_pagination(
    monkeypatch,
) -> None:
    captured_body = {}
    cache_search_response = AsyncMock()

    class FakeClient:
        async def head(self, path: str):
            return SimpleNamespace(
                status_code=200,
                raise_for_status=lambda: None,
            )

        async def post(self, path: str, json: dict):
            captured_body.update(json)
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {"hits": {"total": {"value": 25}, "hits": []}},
            )

    monkeypatch.setattr(search_index, "get_search_client", lambda: FakeClient())
    monkeypatch.setattr(
        search_index,
        "get_cached_search_response",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        search_index,
        "cache_search_response",
        cache_search_response,
    )

    result = await search_index.search_documents(
        "python",
        page=3,
        page_size=10,
    )

    assert captured_body["from"] == 20
    assert captured_body["size"] == 10
    assert captured_body["query"] == {
        "multi_match": {
            "query": "python",
            "fields": ["text"],
        }
    }
    assert result == {
        "query": "python",
        "total": 25,
        "page": 3,
        "page_size": 10,
        "results": [],
    }
    cache_search_response.assert_awaited_once_with(
        "python",
        3,
        10,
        result,
    )


@pytest.mark.anyio
async def test_search_documents_returns_cached_response(monkeypatch) -> None:
    cached_response = {
        "query": "python",
        "total": 1,
        "page": 1,
        "page_size": 10,
        "results": [
            {
                "chunk_id": "document-id:1",
                "file_name": "document.pdf",
                "page": 1,
                "text": "Python text",
                "score": 1.0,
            }
        ],
    }
    monkeypatch.setattr(
        search_index,
        "get_cached_search_response",
        AsyncMock(return_value=cached_response),
    )
    monkeypatch.setattr(
        search_index,
        "get_search_client",
        lambda: pytest.fail("Elasticsearch should not be called"),
    )

    result = await search_index.search_documents(
        "python",
        page=1,
        page_size=10,
    )

    assert result == cached_response


@pytest.mark.anyio
async def test_cache_search_response_uses_redis_ttl(monkeypatch) -> None:
    captured = {}

    class FakeCacheClient:
        async def set(self, key: str, value: str, ex: int):
            captured["key"] = key
            captured["value"] = value
            captured["ex"] = ex

    response = {
        "query": "python",
        "total": 0,
        "page": 1,
        "page_size": 10,
        "results": [],
    }
    monkeypatch.setattr(
        search_index,
        "get_cache_client",
        lambda: FakeCacheClient(),
    )

    await search_index.cache_search_response("python", 1, 10, response)

    assert captured["key"].startswith("search:")
    assert captured["ex"] == 300
    assert captured["value"] == (
        '{"query": "python", "total": 0, "page": 1, '
        '"page_size": 10, "results": []}'
    )
