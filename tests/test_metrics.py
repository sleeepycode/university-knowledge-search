from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_metrics_endpoint_exposes_search_metrics() -> None:
    client.post("/api/v1/search")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "search_requests_total" in response.text
    assert "search_response_duration_seconds_count" in response.text
    assert "search_response_duration_seconds_sum" in response.text