from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.services.search_index import (
    SearchIndexUnavailableError,
    close_cache_client,
    close_search_client,
    ensure_documents_index,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await ensure_documents_index()
    except SearchIndexUnavailableError:
        logger.warning("Elasticsearch index was not initialized")

    yield

    await close_search_client()
    await close_cache_client()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
