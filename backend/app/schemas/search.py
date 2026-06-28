from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: str
    file_name: str
    page: int
    text: str
    score: float
