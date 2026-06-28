from typing import Any

import httpx
from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.document import Document
from backend.app.services.text_chunker import TextChunk

INDEX_MAPPING: dict[str, Any] = {
    "settings": {
        "analysis": {
            "filter": {
                "russian_stop": {
                    "type": "stop",
                    "stopwords": "_russian_",
                },
                "russian_stemmer": {
                    "type": "stemmer",
                    "language": "russian",
                },
            },
            "analyzer": {
                "analysis-ru": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "russian_stop",
                        "russian_stemmer",
                    ],
                }
            },
        }
    },
    "mappings": {
        "properties": {
            "chunk_id": {"type": "keyword"},
            "file_name": {"type": "text"},
            "page_number": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "analysis-ru",
            },
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
    chunks: list[TextChunk],
) -> None:
    await ensure_documents_index()
    client = get_search_client()

    try:
        for chunk in chunks:
            chunk_id = f"{document.uuid}:{chunk.chunk_number}"
            response = await client.put(
                f"/{settings.elasticsearch_index}/_doc/{chunk_id}",
                json={
                    "chunk_id": chunk_id,
                    "file_name": document.file_name,
                    "page_number": chunk.page_number,
                    "text": chunk.text,
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
                        "fields": ["text"],
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
            "chunk_id": hit["_source"]["chunk_id"],
            "file_name": hit["_source"]["file_name"],
            "page": hit["_source"]["page_number"],
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
