from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.metrics import (
    SEARCH_REQUESTS,
    SEARCH_RESPONSE_DURATION,
)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

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