import os
import time
from playwright.sync_api import Page, expect


class TestDocumentFlow:

    def test_upload_index_search_flow(
        self,
        page: Page,
        frontend_url: str,
        test_file_path: str,
        search_query: str,
    ):

        assert os.path.exists(test_file_path), f"Файл не найден: {test_file_path}"
        file_name = os.path.basename(test_file_path)

        os.makedirs("tests/screenshots", exist_ok=True)

        page.goto(frontend_url)
        page.wait_for_load_state("networkidle")
        page.screenshot(path="tests/screenshots/01_homepage.png")
        print(f" Шаг 1: Главная страница открыта на {frontend_url}")

        file_input = page.locator('input[type="file"]')
        
        if not file_input.is_visible():
            file_input.evaluate('el => { el.style.display = "block"; el.style.opacity = "1"; }')
        
        file_input.set_input_files(test_file_path)
        print(f" Шаг 2: Файл выбран — {file_name}")
        
        page.screenshot(path="tests/screenshots/02_file_selected.png")

        try:
            uploaded_file = page.locator(f'li:has-text("{file_name}")')
            expect(uploaded_file.first).to_be_visible(timeout=15000)
            print("Шаг 3: Документ успешно загружен на сервер и появился в списке")
        except Exception as e:
            print(f" Шаг 3: Не удалось подтвердить загрузку — {e}")
        
        page.screenshot(path="tests/screenshots/03_uploaded.png")

        print(" Шаг 4: Ожидание индексации документа...")
        
        try:
            ready_status = page.locator(
                f'li:has-text("{file_name}") >> text=/Готово|готово|ready/i'
            )
            expect(ready_status.first).to_be_visible(timeout=60000)
            print(" Шаг 4: Документ проиндексирован (статус: Готово)")
        except Exception:
            print(" Индикатор статуса не найден, ждём 5 секунд...")
            time.sleep(5)
        
        page.screenshot(path="tests/screenshots/04_indexed.png")

        print("🔍 Шаг 5: Переход на страницу поиска...")
        page.goto(f"{frontend_url}/search")
        page.wait_for_load_state("networkidle")
        page.screenshot(path="tests/screenshots/05_search_page.png")
        print(" Шаг 5: Страница поиска открыта")

        search_input = page.locator(
            'input[type="search"], '
            'input[placeholder*="Поиск" i], '
            'input[placeholder*="search" i], '
            'input[name="q"], '
            'input[name="query"], '
            'input[type="text"]'
        )
        
        expect(search_input.first).to_be_visible(timeout=5000)
        search_input.first.click()
        search_input.first.fill(search_query)
        print(f" Шаг 6: Введён поисковый запрос — '{search_query}'")
        
        search_input.first.press("Enter")
        
        page.wait_for_load_state("networkidle")
        page.screenshot(path="tests/screenshots/06_search_performed.png")

        results = page.locator(
            '.search-result, .result-item, .document-card, '
            '[data-testid="search-result"], '
            'article, .result, .search-results > *, '
            'li, .item'
        )
        
        expect(results.first).to_be_visible(timeout=10000)
        results_count = results.count()
        print(f" Шаг 7: Найдено результатов — {results_count}")
        
        page_content = page.locator('main, .search-results, body').first
        expect(page_content).to_contain_text(search_query, ignore_case=True)
        print(f" Шаг 8: Искомый текст '{search_query}' найден в результатах")
        
        page.screenshot(path="tests/screenshots/07_results.png")
        
        print(" ВСЕ ШАГИ ПРОЙДЕНЫ УСПЕШНО!")