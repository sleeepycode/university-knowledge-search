from fastapi import APIRouter

from backend.app.api.v1 import documents, health, search

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"],
)
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"],
)
