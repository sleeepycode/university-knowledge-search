from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_search(monkeypatch) -> None:
    search_documents = AsyncMock(
        return_value={
            "query": "python",
            "total": 25,
            "page": 2,
            "page_size": 10,
            "results": [
                {
                    "chunk_id": "d2f76189-0433-4588-9608-8c00586a9e79:1",
                    "file_name": "document.pdf",
                    "page": 1,
                    "text": "Python is used in backend services.",
                    "score": 1.25,
                }
            ],
        }
    )
    monkeypatch.setattr(
        "backend.app.api.v1.search.search_documents",
        search_documents,
    )

    response = client.get("/api/v1/search?q=python&page=2&page_size=10")

    assert response.status_code == 200
    assert response.json() == {
        "query": "python",
        "total": 25,
        "page": 2,
        "page_size": 10,
        "results": [
            {
                "chunk_id": "d2f76189-0433-4588-9608-8c00586a9e79:1",
                "file_name": "document.pdf",
                "page": 1,
                "text": "Python is used in backend services.",
                "score": 1.25,
            }
        ],
    }
    search_documents.assert_awaited_once_with(
        "python",
        page=2,
        page_size=10,
    )


def test_search_defaults_to_first_page(monkeypatch) -> None:
    search_documents = AsyncMock(
        return_value={
            "query": "python",
            "total": 0,
            "page": 1,
            "page_size": 10,
            "results": [],
        }
    )
    monkeypatch.setattr(
        "backend.app.api.v1.search.search_documents",
        search_documents,
    )

    response = client.get("/api/v1/search?q=python")

    assert response.status_code == 200
    assert response.json() == {
        "query": "python",
        "total": 0,
        "page": 1,
        "page_size": 10,
        "results": [],
    }
    search_documents.assert_awaited_once_with(
        "python",
        page=1,
        page_size=10,
    )
