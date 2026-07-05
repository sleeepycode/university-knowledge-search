import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client() -> TestClient:
    """Фикстура для создания клиента тестирования."""
    return TestClient(app)


def test_health_check_success(client: TestClient) -> None:
    """Тест успешного выполнения health check."""
    response = client.get("/api/v1/health")
    
    # Проверка статуса
    assert response.status_code == 200
    
    # Проверка структуры ответа
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    
    # Проверка типа данных
    assert isinstance(data, dict)
    assert isinstance(data["status"], str)


def test_health_check_response_headers(client: TestClient) -> None:
    """Тест заголовков ответа health check."""
    response = client.get("/api/v1/health")
    
    # Проверка Content-Type
    assert response.headers["content-type"] == "application/json"
    assert "content-length" in response.headers


def test_health_check_response_time(client: TestClient) -> None:
    """Тест времени ответа health check."""
    import time
    
    start_time = time.time()
    response = client.get("/api/v1/health")
    elapsed_time = time.time() - start_time
    
    assert response.status_code == 200
    # Проверяем, что ответ приходит быстро (менее 1 секунды)
    assert elapsed_time < 1.0


def test_health_check_invalid_method(client: TestClient) -> None:
    """Тест использования недопустимого HTTP метода."""
    methods_to_test = ["POST", "PUT", "DELETE", "PATCH"]
    
    for method in methods_to_test:
        response = client.request(method, "/api/v1/health")
        assert response.status_code == 405  # Method Not Allowed


@pytest.mark.parametrize("headers,expected_status", [
    ({}, 200),  # Без заголовков
    ({"Accept": "application/json"}, 200),  # С Accept заголовком
    ({"Accept": "text/plain"}, 200),  # Нестандартный Accept
    ({"User-Agent": "CustomBot/1.0"}, 200),  # С User-Agent
])
def test_health_check_with_headers(
    client: TestClient, 
    headers: dict, 
    expected_status: int
) -> None:
    """Тест health check с различными заголовками."""
    response = client.get("/api/v1/health", headers=headers)
    assert response.status_code == expected_status
    if response.status_code == 200:
        assert response.json()["status"] == "ok"


def test_health_check_multiple_requests(client: TestClient) -> None:
    """Тест множественных запросов к health check."""
    for i in range(5):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_health_check_unicode_accept(client: TestClient) -> None:
    """Тест health check с Unicode в Accept заголовке."""
    response = client.get(
        "/api/v1/health",
        headers={"Accept": "application/json; charset=utf-8"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_check_api_version_header(client: TestClient) -> None:
    """Тест health check с заголовком версии API."""
    response = client.get(
        "/api/v1/health",
        headers={"X-API-Version": "1.0"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_check_with_compression(client: TestClient) -> None:
    """Тест health check с поддержкой сжатия."""
    response = client.get(
        "/api/v1/health",
        headers={"Accept-Encoding": "gzip, deflate, br"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"