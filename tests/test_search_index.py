from types import SimpleNamespace

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
async def test_search_documents_uses_multi_match_by_text(monkeypatch) -> None:
    captured_body = {}

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
                json=lambda: {"hits": {"hits": []}},
            )

    monkeypatch.setattr(search_index, "get_search_client", lambda: FakeClient())

    await search_index.search_documents("python")

    assert captured_body["query"] == {
        "multi_match": {
            "query": "python",
            "fields": ["text"],
        }
    }
