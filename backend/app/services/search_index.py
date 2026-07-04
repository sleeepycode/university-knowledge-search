import hashlib
import json
from typing import Any

import httpx
from fastapi import HTTPException, status
from redis.asyncio import Redis
from redis.exceptions import RedisError

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
_cache_client: Redis | None = None


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


def get_cache_client() -> Redis:
    global _cache_client
    if _cache_client is None:
        _cache_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )
    return _cache_client


async def close_cache_client() -> None:
    global _cache_client
    if _cache_client is not None:
        await _cache_client.aclose()
        _cache_client = None


def build_search_cache_key(
    query: str,
    page: int,
    page_size: int,
) -> str:
    key_payload = json.dumps(
        {
            "query": query,
            "page": page,
            "page_size": page_size,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    key_hash = hashlib.sha256(key_payload.encode("utf-8")).hexdigest()
    return f"search:{key_hash}"


async def get_cached_search_response(
    query: str,
    page: int,
    page_size: int,
) -> dict[str, Any] | None:
    try:
        cached_response = await get_cache_client().get(
            build_search_cache_key(query, page, page_size)
        )
    except RedisError:
        return None

    if cached_response is None:
        return None

    try:
        return json.loads(cached_response)
    except json.JSONDecodeError:
        return None


async def cache_search_response(
    query: str,
    page: int,
    page_size: int,
    response: dict[str, Any],
) -> None:
    try:
        await get_cache_client().set(
            build_search_cache_key(query, page, page_size),
            json.dumps(response, ensure_ascii=False),
            ex=settings.search_cache_ttl_seconds,
        )
    except RedisError:
        return


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


async def search_documents(
    query: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    cached_response = await get_cached_search_response(
        query,
        page,
        page_size,
    )
    if cached_response is not None:
        return cached_response

    await ensure_documents_index()
    client = get_search_client()
    offset = (page - 1) * page_size

    try:
        response = await client.post(
            f"/{settings.elasticsearch_index}/_search",
            json={
                "from": offset,
                "size": page_size,
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
    hits = response_body["hits"]
    total = hits["total"]
    if isinstance(total, dict):
        total_value = total["value"]
    else:
        total_value = total

    search_response = {
        "query": query,
        "total": total_value,
        "page": page,
        "page_size": page_size,
        "results": [
            {
                "chunk_id": hit["_source"]["chunk_id"],
                "file_name": hit["_source"]["file_name"],
                "page": hit["_source"]["page_number"],
                "text": hit["_source"]["text"],
                "score": hit["_score"],
            }
            for hit in hits["hits"]
        ],
    }
    await cache_search_response(query, page, page_size, search_response)
    return search_response


def search_index_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Search index is unavailable",
    )
