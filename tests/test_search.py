from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_search(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.app.api.v1.search.search_documents",
        AsyncMock(
            return_value=[
                {
                    "document_uuid": "d2f76189-0433-4588-9608-8c00586a9e79",
                    "file_name": "document.pdf",
                    "chunk_number": 1,
                    "text": "Python is used in backend services.",
                    "score": 1.25,
                }
            ]
        ),
    )

    response = client.get("/api/v1/search?q=python")

    assert response.status_code == 200
    assert response.json() == {
        "query": "python",
        "results": [
            {
                "document_uuid": "d2f76189-0433-4588-9608-8c00586a9e79",
                "file_name": "document.pdf",
                "chunk_number": 1,
                "text": "Python is used in backend services.",
                "score": 1.25,
            }
        ],
    }
