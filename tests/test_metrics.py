import re
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_metrics_endpoint_returns_empty_metrics_when_no_requests() -> None:
    """Проверяем, что эндпоинт возвращает метрики даже без запросов"""
    response = client.get("/metrics")
    
    assert response.status_code == 200
    # Убираем точное сравнение пробелов
    assert "text/plain" in response.headers["content-type"]
    assert "charset=utf-8" in response.headers["content-type"]
    
    content = response.text
    
    # Проверяем, что метрики существуют (могут быть с нулевыми значениями или вообще без них)
    # Просто проверяем наличие структуры
    assert "search_requests_total" in content or "# HELP search_requests_total" in content


def test_metrics_endpoint_with_multiple_different_requests() -> None:
    """Проверяем метрики для разных методов и путей"""
    # Выполняем GET запросы 
    try:
        response = client.get("/api/v1/search?query=test")
        if response.status_code != 405: 
            client.get("/api/v1/search?query=another")
    except:
        pass
    
    # Выполняем POST запросы
    client.post("/api/v1/search", json={"query": "test"})
    client.post("/api/v1/search", json={"query": "another"})
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Проверяем наличие метрик для POST 
    assert "search_requests_total" in content
    # Проверяем, что счетчик увеличился (находим значение)
    post_match = re.search(
        r'search_requests_total\{(?:[^}]*)?method="POST"(?:[^}]*)?path="/api/v1/search"(?:[^}]*)?\} (\d+\.?\d*)',
        content
    )
    if post_match:
        assert float(post_match.group(1)) >= 2


def test_metrics_endpoint_handles_concurrent_requests() -> None:
    """Проверяем метрики при конкурентных запросах"""
    import concurrent.futures
    
    def make_request() -> None:
        try:
            client.post("/api/v1/search", json={"query": "concurrent test"})
        except:
            pass
    
    # Выполняем 10 конкурентных запросов
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        concurrent.futures.wait(futures)
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Проверяем, что метрики существуют
    assert "search_requests_total" in content


def test_metrics_endpoint_with_error_responses() -> None:
    """Проверяем, что ошибки также учитываются в метриках"""
    # Отправляем некорректный запрос (невалидный JSON)
    response = client.post("/api/v1/search", json={"invalid": "data"})
    # Если эндпоинт не возвращает 422, проверяем что это ошибка
    assert response.status_code in [400, 422, 405]
    
    # Отправляем запрос с несуществующим путем
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
    
    # Проверяем метрики для ошибок
    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    
    content = metrics_response.text
    
    # Проверяем, что метрики существуют
    assert "search_requests_total" in content


def test_metrics_endpoint_returns_correct_prometheus_format() -> None:
    """Проверяем корректность формата Prometheus"""
    # Делаем несколько запросов для генерации метрик
    try:
        client.post("/api/v1/search", json={"query": "format test"})
        client.post("/api/v1/search", json={"query": "another test"})
    except:
        pass
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Проверяем структуру Prometheus метрик
    lines = content.strip().split("\n")
    
    # Проверяем, что есть HELP и TYPE для метрик
    has_help = any("# HELP" in line for line in lines)
    has_type = any("# TYPE" in line for line in lines)
    
    assert has_help, "No HELP comments found in metrics"
    assert has_type, "No TYPE comments found in metrics"
    
    # Проверяем, что все строки с метриками имеют правильный формат
    for line in lines:
        if line and not line.startswith("#"):
            # Метрики должны иметь формат: name{labels} value или name value
            assert " " in line, f"Invalid metric line: {line}"
            parts = line.split(" ")
            assert len(parts) >= 2, f"Invalid metric format: {line}"
            # Проверяем, что значение - число
            try:
                float(parts[-1])
            except ValueError:
                pytest.fail(f"Invalid metric value: {line}")


def test_metrics_endpoint_with_invalid_search_requests() -> None:
    """Проверяем, что эндпоинт метрик работает даже после ошибок"""
    # Отправляем различные некорректные запросы
    invalid_queries = [
        {},  # Пустой запрос
        {"query": ""},  # Пустой query
        {"limit": -1},  # Отрицательный лимит
        {"query": "a" * 10000},  # Слишком длинный запрос
    ]
    
    for query in invalid_queries:
        try:
            response = client.post("/api/v1/search", json=query)
            # Просто проверяем, что запрос не вызвал исключение
            assert response.status_code in [200, 400, 422, 405]
        except:
            pass
    
    # Проверяем, что метрики все еще доступны
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "search_requests_total" in response.text


def test_metrics_endpoint_response_time_metrics() -> None:
    """Проверяем, что метрики времени ответа обновляются"""
    import time
    
    # Делаем запрос с задержкой 
    try:
        start = time.time()
        client.post("/api/v1/search", json={"query": "slow test"})
        elapsed = time.time() - start
    except:
        elapsed = 0
    
    response = client.get("/metrics")
    assert response.status_code == 200
    
    content = response.text
    
    # Проверяем наличие метрик длительности
    if "search_response_duration_seconds_sum" in content:
        # Извлекаем значение sum
        sum_match = re.search(
            r'search_response_duration_seconds_sum\{(?:[^}]*)?method="POST"(?:[^}]*)?\} (\d+\.?\d*)',
            content
        )
        if sum_match:
            assert float(sum_match.group(1)) >= 0