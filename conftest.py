import pytest
import os


@pytest.fixture(scope="session")
def frontend_url():
    """URL фронтенда"""
    return "http://localhost:3000"


@pytest.fixture(scope="session")
def api_url():
    """URL бэкенда"""
    return "http://127.0.0.1:8000"


@pytest.fixture
def test_file_path():
    """Путь к тестовому .docx файлу"""
    return os.path.abspath("tests/e2e/fixtures/valid.docx")


@pytest.fixture
def search_query():
    """Текст для поиска"""
    return "look for your shadow"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Автоматический скриншот при падении теста"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            os.makedirs("tests/screenshots", exist_ok=True)
            screenshot_path = f"tests/screenshots/{item.name}_failed.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n📸 Скриншот ошибки сохранён: {screenshot_path}")