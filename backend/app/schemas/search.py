import uuid

from pydantic import BaseModel


class SearchResult(BaseModel):
    document_uuid: uuid.UUID
    file_name: str
    chunk_number: int
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
