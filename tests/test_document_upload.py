import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.db.session import get_db_session
from backend.app.main import app
from backend.app.services.document_processing import ProcessingResult
from backend.app.services.search_index import SearchIndexUnavailableError
from backend.app.services.text_chunker import TextChunk


async def override_db_session():
    yield AsyncMock()


app.dependency_overrides[get_db_session] = override_db_session
client = TestClient(app)


def test_upload_pdf(monkeypatch) -> None:
    content = b"%PDF-1.4 test document"
    document_uuid = uuid.uuid4()
    created_at = datetime.now(UTC)
    monkeypatch.setattr(
        "backend.app.api.v1.documents.process_document",
        AsyncMock(
            return_value=ProcessingResult(
                text="PDF document text",
                chunks=[
                    TextChunk(
                        chunk_number=1,
                        page_number=1,
                        text="PDF document text",
                    )
                ],
            )
        ),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.save_document",
        AsyncMock(
            return_value=SimpleNamespace(
                id=1,
                uuid=document_uuid,
                file_name="document.pdf",
                file_path=f"uploads/{document_uuid}.pdf",
                created_at=created_at,
            )
        ),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.index_document_chunks",
        AsyncMock(),
    )

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("document.pdf", content, "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "uuid": str(document_uuid),
        "file_name": "document.pdf",
        "file_path": f"uploads/{document_uuid}.pdf",
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "extracted_characters": 17,
        "chunks_count": 1,
    }


def test_upload_docx(monkeypatch) -> None:
    content = b"test docx content"
    document_uuid = uuid.uuid4()
    monkeypatch.setattr(
        "backend.app.api.v1.documents.process_document",
        AsyncMock(
            return_value=ProcessingResult(
                text="DOCX document text",
                chunks=[
                    TextChunk(
                        chunk_number=1,
                        page_number=1,
                        text="DOCX document text",
                    )
                ],
            )
        ),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.save_document",
        AsyncMock(
            return_value=SimpleNamespace(
                id=2,
                uuid=document_uuid,
                file_name="document.DOCX",
                file_path=f"uploads/{document_uuid}.docx",
                created_at=datetime.now(UTC),
            )
        ),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.index_document_chunks",
        AsyncMock(),
    )

    response = client.post(
        "/api/v1/documents/upload",
        files={
            "file": (
                "document.DOCX",
                content,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["file_name"] == "document.DOCX"


def test_upload_removes_saved_document_when_search_index_is_unavailable(
    monkeypatch,
) -> None:
    content = b"%PDF-1.4 test document"
    document_uuid = uuid.uuid4()
    saved_document = SimpleNamespace(
        id=3,
        uuid=document_uuid,
        file_name="document.pdf",
        file_path=f"uploads/{document_uuid}.pdf",
        created_at=datetime.now(UTC),
    )
    delete_saved_document = AsyncMock()
    monkeypatch.setattr(
        "backend.app.api.v1.documents.process_document",
        AsyncMock(
            return_value=ProcessingResult(
                text="PDF document text",
                chunks=[
                    TextChunk(
                        chunk_number=1,
                        page_number=1,
                        text="PDF document text",
                    )
                ],
            )
        ),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.save_document",
        AsyncMock(return_value=saved_document),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.index_document_chunks",
        AsyncMock(side_effect=SearchIndexUnavailableError()),
    )
    monkeypatch.setattr(
        "backend.app.api.v1.documents.delete_saved_document",
        delete_saved_document,
    )

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("document.pdf", content, "application/pdf")},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "Search index is unavailable"}
    delete_saved_document.assert_awaited_once()
    assert delete_saved_document.await_args.args[0] is saved_document


def test_wrong_extension() -> None:
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", b"text", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": "Only PDF and DOCX files are allowed"
    }


def test_big_file() -> None:
    content = b"x" * (settings.max_upload_size_bytes + 1)

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("large.pdf", content, "application/pdf")},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "File size must not exceed 20 MB"
    }
