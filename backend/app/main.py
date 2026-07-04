from contextlib import asynccontextmanager
import logging
from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.metrics import (
    SEARCH_REQUESTS,
    SEARCH_RESPONSE_DURATION,
)
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

    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    @app.middleware("http")
    async def collect_search_metrics(
        request: Request,
        call_next,
    ):
        search_path = f"{settings.api_v1_prefix}/search"

        if request.url.path != search_path:
            return await call_next(request)

        started_at = perf_counter()
        SEARCH_REQUESTS.inc()

        try:
            return await call_next(request)
        finally:
            SEARCH_RESPONSE_DURATION.observe(
                perf_counter() - started_at,
            )

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(
            content=generate_latest(),
            headers={
                "Content-Type": CONTENT_TYPE_LATEST,
            },
        )

    return app


app = create_app()
