from typing import Any

import httpx
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.document import Document

INDEX_MAPPING: dict[str, Any] = {
    "mappings": {
        "properties": {
            "document_uuid": {"type": "keyword"},
            "file_name": {"type": "text"},
            "chunk_number": {"type": "integer"},
            "text": {"type": "text"},
        }
    }
}


class SearchIndexUnavailableError(RuntimeError):
    pass


_client: httpx.AsyncClient | None = None


def get_search_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=settings.elasticsearch_url.rstrip("/"),
            timeout=10.0,
        )
    return _client


async def close_search_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def ensure_documents_index() -> None:
    client = get_search_client()
    try:
        response = await client.head(f"/{settings.elasticsearch_index}")
        if response.status_code == status.HTTP_404_NOT_FOUND:
            create_response = await client.put(
                f"/{settings.elasticsearch_index}",
                json=INDEX_MAPPING,
            )
            create_response.raise_for_status()
        else:
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise SearchIndexUnavailableError(
            "Elasticsearch is unavailable"
        ) from error


async def index_document_chunks(
    document: Document,
    chunks: list[str],
) -> None:
    await ensure_documents_index()
    client = get_search_client()

    try:
        for chunk_number, chunk in enumerate(chunks, start=1):
            response = await client.put(
                f"/{settings.elasticsearch_index}/_doc/{document.uuid}:{chunk_number}",
                json={
                    "document_uuid": str(document.uuid),
                    "file_name": document.file_name,
                    "chunk_number": chunk_number,
                    "text": chunk,
                },
            )
            response.raise_for_status()
    except httpx.HTTPError as error:
        raise SearchIndexUnavailableError(
            "Could not index document chunks"
        ) from error


async def search_documents(query: str) -> list[dict[str, Any]]:
    await ensure_documents_index()
    client = get_search_client()

    try:
        response = await client.post(
            f"/{settings.elasticsearch_index}/_search",
            json={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["text", "file_name"],
                    }
                }
            },
        )
        response.raise_for_status()
    except httpx.HTTPError as error:
        raise SearchIndexUnavailableError(
            "Could not search documents"
        ) from error

    response_body = response.json()
    return [
        {
            "document_uuid": hit["_source"]["document_uuid"],
            "file_name": hit["_source"]["file_name"],
            "chunk_number": hit["_source"]["chunk_number"],
            "text": hit["_source"]["text"],
            "score": hit["_score"],
        }
        for hit in response_body["hits"]["hits"]
    ]


def search_index_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Search index is unavailable",
    )
