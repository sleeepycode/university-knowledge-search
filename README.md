# University Knowledge Search

Веб-приложение для загрузки учебных документов, извлечения текста и полнотекстового поиска по внутренней базе знаний университета.

Система позволяет загрузить PDF/DOCX-документы, автоматически извлечь из них текст, разбить его на фрагменты, проиндексировать в Elasticsearch и искать по этим материалам через веб-интерфейс.

## Содержание

- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Состав проекта](#состав-проекта)
- [Backend](#backend)
- [Frontend](#frontend)
- [DevOps](#devops)
- [QA и тестирование](#qa-и-тестирование)
- [Запуск проекта](#запуск-проекта)
- [API](#api)
- [Проверка данных](#проверка-данных)
- [Частые проблемы](#частые-проблемы)

## Стек технологий

| Часть | Технологии | Назначение |
|---|---|---|
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy, Alembic | REST API, обработка документов, работа с БД |
| Парсинг документов | pdfplumber, python-docx | извлечение текста из PDF и DOCX |
| База данных | PostgreSQL | хранение документов и истории поиска |
| Поиск | Elasticsearch | полнотекстовый поиск и ранжирование результатов |
| Кеш | Redis | кеширование повторных поисковых запросов |
| Frontend | React, TypeScript, Vite, Bun | пользовательский интерфейс |
| Web server | Nginx | отдача собранного frontend и проксирование API |
| DevOps | Docker, Docker Compose, GitHub Actions | сборка, запуск и CI |
| Monitoring | Prometheus, Grafana | сбор и отображение метрик поиска |
| QA | Pytest, Playwright, Locust, Ruff, Oxlint | unit/integration/e2e/load проверки |

## Архитектура

Проект запускается через Docker Compose и включает несколько сервисов.

| Сервис | Назначение | Локальный адрес |
|---|---|---|
| `front` | React frontend через Nginx | `http://localhost:3000` |
| `app` | FastAPI backend | `http://localhost:8000` |
| `postgres` | документы и история поиска | `localhost:5432` или `localhost:5433` |
| `elasticsearch` | поисковый индекс | `http://localhost:9200` |
| `redis` | кеш поисковых запросов | `localhost:6379` |
| `prometheus` | сбор метрик | `http://localhost:9090` |
| `grafana` | дашборды метрик | `http://localhost:3001` |

Общий сценарий работы:

1. Пользователь загружает PDF или DOCX через frontend.
2. Backend проверяет формат и размер файла.
3. Текст извлекается из документа.
4. Текст делится на чанки по 1000 символов с перекрытием 100 символов.
5. Информация о документе сохраняется в PostgreSQL.
6. Чанки индексируются в Elasticsearch.
7. Пользователь вводит поисковый запрос.
8. Backend ищет релевантные фрагменты в Elasticsearch.
9. Результаты возвращаются на frontend карточками.
10. Повторные запросы кешируются в Redis.
11. Успешные поисковые запросы сохраняются в историю.

## Состав проекта

```text
backend/                  # FastAPI backend
frontend/                 # React frontend
migrations/               # Alembic migrations
monitoring/               # Prometheus и Grafana
tests/                    # backend, e2e и нагрузочные тесты
.github/workflows/ci.yml  # CI pipeline
docker-compose.yml        # запуск всех сервисов
.env.example              # пример переменных окружения
init.sh                   # скрипт начального наполнения
```

## Backend

Backend реализует API и основную серверную логику.

Основные возможности:

- загрузка документов через `POST /api/v1/documents/upload`;
- проверка PDF/DOCX и ограничения 20 MB;
- генерация UUID для документа;
- извлечение текста из PDF и DOCX;
- разбиение текста на чанки;
- сохранение документов в PostgreSQL;
- создание и настройка индекса Elasticsearch;
- индексация чанков с метаданными;
- поиск через `GET /api/v1/search`;
- пагинация результатов поиска;
- кеширование частых запросов через Redis;
- сохранение истории поиска;
- Swagger/OpenAPI-документация;
- экспорт метрик Prometheus.

Основные backend-файлы:

```text
backend/app/main.py
backend/app/api/v1/documents.py
backend/app/api/v1/search.py
backend/app/services/document_processing.py
backend/app/services/document_upload.py
backend/app/services/search_index.py
backend/app/models/document.py
backend/app/models/search_history.py
```

Swagger-документация:

```text
http://localhost:8000/docs
```

OpenAPI JSON:

```text
http://localhost:8000/openapi.json
```

## Frontend

Frontend реализован на React и TypeScript.

Основные возможности:

- drag-and-drop загрузка документов;
- отображение прогресса загрузки и статуса индексации;
- список загруженных документов;
- поле поиска;
- запуск поиска по кнопке и Enter;
- вывод результатов карточками;
- подсветка совпадений;
- пагинация результатов;
- отображение ошибок API.

Основные frontend-файлы:

```text
frontend/src/api/client.ts
frontend/src/components/FileUpload.tsx
frontend/src/components/SearchResult.tsx
frontend/src/pages/HomePage.tsx
frontend/src/pages/SearchPage.tsx
frontend/src/utils/highlight.ts
```

Локальные команды frontend:

```bash
cd frontend
bun install
bun run dev
bun run test
bun run build
```

## DevOps

DevOps-часть отвечает за воспроизводимый запуск и проверку проекта.

Реализовано:

- `backend/Dockerfile` для FastAPI;
- `frontend/Dockerfile` для сборки frontend и запуска через Nginx;
- `frontend/nginx.conf` для SPA и проксирования API;
- `docker-compose.yml` для запуска всего стека;
- `.env.example` для переменных окружения;
- healthcheck для основных сервисов;
- автоматический запуск миграций Alembic перед стартом backend;
- GitHub Actions для backend/frontend/docker проверок;
- Prometheus и Grafana для мониторинга;
- `init.sh` для загрузки тестовых PDF-документов.

CI выполняет:

| Job | Что проверяет |
|---|---|
| `backend` | установка зависимостей, Ruff, Pytest |
| `frontend` | Bun install, Oxlint, frontend tests, build |
| `docker` | `docker compose config`, сборка образов `app` и `front` |

## QA и тестирование

В проекте есть несколько уровней тестирования.

### Backend unit/integration tests

Запуск:

```bash
python -m pytest
```

Отдельные наборы:

```bash
python -m pytest tests/test_document_upload.py
python -m pytest tests/test_search.py
python -m pytest tests/test_search_index.py
python -m pytest tests/test_health.py
python -m pytest tests/test_metrics.py
```

Что проверяют backend-тесты:

| Файл | Что проверяет |
|---|---|
| `tests/test_document_upload.py` | загрузку PDF/DOCX, валидацию формата и размера, удаление документа при недоступном Elasticsearch, список документов |
| `tests/test_search.py` | поиск, параметры пагинации, сохранение истории поиска, endpoint истории |
| `tests/test_search_index.py` | mapping Elasticsearch, русский анализатор, multi_match, пагинацию, Redis-кеш |
| `tests/test_health.py` | endpoint `GET /api/v1/health`, формат ответа, заголовки, время ответа, недопустимые HTTP-методы |
| `tests/test_metrics.py` | endpoint `/metrics`, Prometheus-формат, наличие счетчиков и гистограмм, устойчивость после ошибочных запросов |

### Frontend tests

Запуск:

```bash
cd frontend
bun run test
```

Основной frontend-тест:

| Файл | Что проверяет |
|---|---|
| `frontend/src/utils/highlight.test.ts` | подсветку совпадений, несколько слов в запросе, пустой запрос, HTML escaping, спецсимволы regex и локализацию статусов |

### E2E tests

E2E-тесты находятся в `tests/e2e`.

Они проверяют полный пользовательский сценарий:

1. открытие frontend;
2. выбор тестового документа;
3. загрузку файла;
4. ожидание индексации;
5. переход на страницу поиска;
6. ввод поискового запроса;
7. появление результатов;
8. наличие искомого текста в результатах.

Файл:

```text
tests/e2e/test_document_flow.py
```

Фикстуры:

```text
conftest.py
tests/e2e/fixtures/
```

В корневом `conftest.py` заданы адрес frontend, адрес API, путь к тестовому документу и поисковый запрос. По умолчанию используется frontend `http://localhost:3000`, файл `tests/e2e/fixtures/valid.docx` и запрос `look for your shadow`.

Перед запуском e2e нужно поднять проект:

```bash
docker compose up --build -d
```

Затем установить браузеры Playwright, если они еще не установлены:

```bash
python -m playwright install
```

Запуск:

```bash
python -m pytest tests/e2e
```

Обычная команда `python -m pytest` запускает backend-тесты и игнорирует e2e по настройке `pytest.ini`.

E2E-тест сохраняет скриншоты шагов в:

```text
tests/screenshots/
```

### Load tests

Нагрузочный тест находится в:

```text
tests/locust_test/locustfile.py
```

Он отправляет поисковые запросы на:

```text
/api/v1/search
```

Запуск:

```bash
locust -f tests/locust_test/locustfile.py --host http://localhost:8000
```

После запуска интерфейс Locust доступен по адресу:

```text
http://localhost:8089
```

### Linting

Backend:

```bash
ruff check backend tests
```

Frontend:

```bash
cd frontend
bunx oxlint@1.72.0 src
```

## Запуск проекта

### 1. Клонирование

```bash
git clone https://github.com/sleeepycode/university-knowledge-search.git
cd university-knowledge-search
```

Для интеграционной ветки:

```bash
git switch dev
git pull
```

### 2. Настройка `.env`

Linux, macOS или Git Bash:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Если порт PostgreSQL `5432` занят локальной базой, поменяйте внешний порт в `.env`:

```env
POSTGRES_PORT=5433
```

### 3. Запуск Docker Compose

```bash
docker compose up --build -d
```

Проверка контейнеров:

```bash
docker compose ps
```

Остановка:

```bash
docker compose down
```

Остановка с удалением данных:

```bash
docker compose down -v
```

Команда `docker compose down -v` удаляет volumes PostgreSQL, Elasticsearch, Redis, Prometheus и Grafana.

## API

| Метод | Endpoint | Назначение |
|---|---|---|
| `GET` | `/api/v1/health` | состояние backend |
| `POST` | `/api/v1/documents/upload` | загрузка PDF/DOCX |
| `GET` | `/api/v1/documents` | список документов |
| `GET` | `/api/v1/search` | полнотекстовый поиск |
| `GET` | `/api/v1/search/history` | история поиска |
| `GET` | `/metrics` | метрики Prometheus |

### Health

```bash
curl http://localhost:8000/api/v1/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

### Загрузка документа

```bash
curl \
  --request POST \
  --form "file=@document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

Поддерживаются:

- PDF;
- DOCX.

Максимальный размер:

```text
20 MB
```

### Список документов

```bash
curl http://localhost:8000/api/v1/documents
```

### Поиск

```bash
curl "http://localhost:8000/api/v1/search?q=практика&page=1&page_size=10"
```

Ответ содержит:

- `query`;
- `total`;
- `page`;
- `page_size`;
- `results`;

Каждый элемент `results` содержит:

- `chunk_id`;
- `file_name`;
- `page`;
- `text`;
- `score`.

### История поиска

```bash
curl http://localhost:8000/api/v1/search/history
```

## Проверка данных

### PostgreSQL

Список таблиц:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

Документы:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select id, uuid, file_name, status, created_at from documents order by id desc limit 10;"'
```

История поиска:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select query, results_count, searched_at from search_history order by searched_at desc limit 10;"'
```

### Elasticsearch

Health:

```bash
curl http://localhost:9200/_cluster/health
```

Количество чанков:

```bash
curl http://localhost:9200/documents/_count
```

Mapping:

```bash
curl http://localhost:9200/documents/_mapping
```

### Redis

Проверка:

```bash
docker compose exec redis redis-cli ping
```

Кеш поиска:

```bash
docker compose exec redis redis-cli keys "search:*"
```

### Prometheus

Интерфейс:

```text
http://localhost:9090
```

Метрики backend:

```text
http://localhost:8000/metrics
```

Основные метрики:

```text
search_requests_total
search_response_duration_seconds_count
search_response_duration_seconds_sum
search_response_duration_seconds_bucket
```

### Grafana

Интерфейс:

```text
http://localhost:3001
```

Локальные учетные данные:

```text
Логин: admin
Пароль: change_me
```

## Начальное наполнение

Скрипт `init.sh`:

1. ожидает готовности backend;
2. скачивает 10 открытых PDF;
3. проверяет сигнатуру PDF;
4. загружает документы через API;
5. выводит статистику загрузки;
6. удаляет временные файлы.

Запуск:

```bash
bash init.sh
```

Для другого адреса API:

```bash
API_URL=http://example.com/api/v1 bash init.sh
```

## Частые проблемы

### Порт PostgreSQL занят

Ошибка:

```text
listen tcp 0.0.0.0:5432: bind: address already in use
```

Решение: поменять внешний порт PostgreSQL в `.env`.

```env
POSTGRES_PORT=5433
```

### Не видно загруженный документ в базе

Скорее всего подключение идет к локальной базе на `5432`, а Docker Postgres опубликован на `5433`.

Проверьте параметры подключения:

```text
host: localhost
port: 5433
database: knowledge_search
user: knowledge_user
password: knowledge_password
```

Или смотрите данные через контейнер:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select * from documents;"'
```

### Elasticsearch image invalid reference format

Ошибка возникает, если в `.env` нет `ELASTIC_VERSION`.

Проверьте:

```env
ELASTIC_VERSION=9.4.2
```

### Swagger

Swagger-документация доступна по адресу:

```text
http://localhost:8000/docs
```

Через Swagger можно вручную проверить загрузку документов, поиск и историю запросов.
