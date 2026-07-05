from locust import HttpUser, task, constant

class WebsiteUser(HttpUser):
    # Задаем фиксированное время ожидания (0 секунд) между запросами, 
    # чтобы пользователи генерировали плотный поток нагрузки.
    wait_time = constant(0)

    @task
    def search_request(self):
        # Отправляем GET-запрос на нужный эндпоинт
        self.client.get("/api/v1/search")