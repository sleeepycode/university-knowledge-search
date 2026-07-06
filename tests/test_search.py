from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient

from backend.app.db.session import get_db_session
from backend.app.main import app

client = TestClient(app)


async def override_db_session():
    yield AsyncMock()


app.dependency_overrides[get_db_session] = override_db_session


def test_search(monkeypatch) -> None:
    session = SimpleNamespace(add=Mock(), commit=AsyncMock())

    async def override_search_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_search_db_session
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

    try:
        response = client.get("/api/v1/search?q=python&page=2&page_size=10")
    finally:
        app.dependency_overrides[get_db_session] = override_db_session

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
    session.add.assert_called_once()
    session.commit.assert_awaited_once()


def test_search_defaults_to_first_page(monkeypatch) -> None:
    session = SimpleNamespace(add=Mock(), commit=AsyncMock())

    async def override_search_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_search_db_session
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

    try:
        response = client.get("/api/v1/search?q=python")
    finally:
        app.dependency_overrides[get_db_session] = override_db_session

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
    session.add.assert_called_once()
    session.commit.assert_awaited_once()


def test_search_history() -> None:
    searched_at = datetime.now(UTC)
    history = [
        SimpleNamespace(
            query="python",
            searched_at=searched_at,
            results_count=3,
        )
    ]
    scalars_result = SimpleNamespace(all=lambda: history)
    query_result = SimpleNamespace(scalars=lambda: scalars_result)
    session = AsyncMock()
    session.execute.return_value = query_result

    async def override_history_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_history_db_session
    try:
        response = client.get("/api/v1/search/history")
    finally:
        app.dependency_overrides[get_db_session] = override_db_session

    assert response.status_code == 200
    assert response.json() == {
        "history": [
            {
                "query": "python",
                "searched_at": searched_at.isoformat().replace("+00:00", "Z"),
                "results_count": 3,
            }
        ]
    }
