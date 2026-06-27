from typing import Annotated

from fastapi import APIRouter, Query

from backend.app.schemas.search import SearchResponse
from backend.app.services.search_index import (
    SearchIndexUnavailableError,
    search_documents,
    search_index_error,
)

router = APIRouter()


@router.get("", response_model=SearchResponse)
async def search(
    q: Annotated[
        str,
        Query(
            min_length=1,
            description="Search query",
        ),
    ],
) -> SearchResponse:
    try:
        results = await search_documents(q)
    except SearchIndexUnavailableError as error:
        raise search_index_error() from error

    return SearchResponse(query=q, results=results)
