import random
from locust import HttpUser, task, constant

class WebsiteUser(HttpUser):
    wait_time = constant(0)

    @task
    def search_request(self):
        # Массив тестовых запросов
        queries = [
            "документ",
            "отчёт",
            "инструкция",
            "правила",
            "политика"
        ]
        
        self.client.get(
            "/api/v1/search",
            params={
                "q": random.choice(queries),
                "page": 1,
                "page_size": 10
            }
        )