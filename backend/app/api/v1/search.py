from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.db.session import get_db_session
from backend.app.models.search_history import SearchHistory
from backend.app.schemas.search import (
    SearchHistoryItem,
    SearchHistoryResponse,
    SearchResponse,
)
from backend.app.services.search_index import (
    SearchIndexUnavailableError,
    search_documents,
    search_index_error,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/history", response_model=SearchHistoryResponse)
async def get_search_history(session: DatabaseSession) -> SearchHistoryResponse:
    result = await session.execute(
        select(SearchHistory).order_by(SearchHistory.searched_at.desc())
    )
    history = result.scalars().all()

    return SearchHistoryResponse(
        history=[
            SearchHistoryItem(
                query=item.query,
                searched_at=item.searched_at,
                results_count=item.results_count,
            )
            for item in history
        ]
    )


@router.get("", response_model=SearchResponse)
async def search(
    session: DatabaseSession,
    q: Annotated[
        str,
        Query(
            min_length=1,
            description="Search query",
        ),
    ],
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Search results page number",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Search results per page",
        ),
    ] = 10,
) -> SearchResponse:
    try:
        results = await search_documents(q, page=page, page_size=page_size)
    except SearchIndexUnavailableError as error:
        raise search_index_error() from error

    session.add(
        SearchHistory(
            query=q,
            results_count=results["total"],
        )
    )
    await session.commit()

    return results
