from prometheus_client import Counter, Histogram


SEARCH_REQUESTS = Counter(
    "search_requests",
    "Total number of requests to the search endpoint",
)

SEARCH_RESPONSE_DURATION = Histogram(
    "search_response_duration_seconds",
    "Search endpoint response duration in seconds",
    buckets=(
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
)