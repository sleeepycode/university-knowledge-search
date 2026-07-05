from datetime import datetime

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: str
    file_name: str
    page: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    total: int
    page: int
    page_size: int
    results: list[SearchResult]


class SearchHistoryItem(BaseModel):
    query: str
    searched_at: datetime
    results_count: int


class SearchHistoryResponse(BaseModel):
    history: list[SearchHistoryItem]
