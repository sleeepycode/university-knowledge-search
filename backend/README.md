# Backend University Knowledge Search

Backend-часть веб-приложения для загрузки университетских документов, извлечения текста, индексации фрагментов и полнотекстового поиска по учебным материалам.

## Назначение

Backend отвечает за:

- загрузку документов PDF и DOCX;
- проверку формата и размера файла;
- сохранение сведений о документах в PostgreSQL;
- извлечение текста из документов;
- разбиение текста на чанки;
- индексацию чанков в Elasticsearch;
- полнотекстовый поиск с ранжированием;
- пагинацию результатов поиска;
- кеширование повторных запросов через Redis;
- сохранение истории поисковых запросов;
- отдачу метрик для Prometheus.

## Архитектура backend

Основные компоненты backend-части:

| Компонент | Назначение |
|---|---|
| `FastAPI` | REST API приложения |
| `PostgreSQL` | хранение документов и истории поиска |
| `Elasticsearch` | полнотекстовый поиск по чанкам |
| `Redis` | кеширование поисковых запросов |
| `Alembic` | миграции базы данных |
| `Prometheus client` | экспорт метрик backend |

## Структура backend

```text
backend/
  app/
    api/v1/          # API endpoints
    core/            # настройки приложения
    db/              # подключение к базе данных
    models/          # SQLAlchemy-модели
    schemas/         # Pydantic-схемы
    services/        # бизнес-логика
    main.py          # создание FastAPI-приложения
    metrics.py       # метрики Prometheus
  Dockerfile

migrations/
  versions/          # Alembic-миграции
```

## Требования

Для запуска через Docker необходимы:

- Docker Desktop;
- Docker Compose;
- файл `.env`.

Для локального запуска без Docker дополнительно нужны:

- Python 3.12;
- установленное виртуальное окружение;
- доступные PostgreSQL, Elasticsearch и Redis.

## Настройка окружения

Скопируйте пример переменных окружения:

```bash
cp .env.example .env
```

На Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Основные переменные backend:

```env
APP_NAME="University Knowledge Search"
APP_ENV=local
API_V1_PREFIX=/api/v1
UPLOAD_DIR=uploads
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
BACKEND_PORT=8000

POSTGRES_DB=knowledge_search
POSTGRES_USER=knowledge_user
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432

ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=documents

REDIS_URL=redis://localhost:6379/0
SEARCH_CACHE_TTL_SECONDS=300
```

Если локальный PostgreSQL уже занимает порт `5432`, можно изменить внешний порт в `.env`:

```env
POSTGRES_PORT=5433
```

Внутри Docker backend всё равно подключается к сервису `postgres` по внутреннему порту `5432`.

## Запуск через Docker Compose

Запустите все сервисы:

```bash
docker compose up --build -d
```

Проверьте состояние контейнеров:

```bash
docker compose ps
```

Backend должен быть доступен по адресу:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

## Локальный запуск backend

Активируйте виртуальное окружение:

```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Примените миграции:

```bash
alembic upgrade head
```

Запустите FastAPI:

```bash
python -m uvicorn backend.app.main:app --reload
```

## API endpoints

| Метод | Endpoint | Назначение |
|---|---|---|
| `GET` | `/api/v1/health` | проверка состояния backend |
| `POST` | `/api/v1/documents/upload` | загрузка PDF/DOCX-документа |
| `GET` | `/api/v1/documents` | список загруженных документов |
| `GET` | `/api/v1/search` | полнотекстовый поиск |
| `GET` | `/api/v1/search/history` | история поисковых запросов |
| `GET` | `/metrics` | метрики Prometheus |

## Проверка состояния backend

```bash
curl http://localhost:8000/api/v1/health
```

Ожидаемый ответ:

```json
{
  "status": "ok"
}
```

## Загрузка документа

Endpoint:

```text
POST /api/v1/documents/upload
```

Пример запроса:

```bash
curl \
  --request POST \
  --form "file=@document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

Поддерживаемые форматы:

- PDF;
- DOCX.

Максимальный размер файла:

```text
20 MB
```

Пример успешного ответа:

```json
{
  "id": 1,
  "uuid": "7ff85440-b40d-4fd7-9241-2f8c5f1e9f3c",
  "file_name": "lecture.pdf",
  "file_path": "/app/uploads/7ff85440-b40d-4fd7-9241-2f8c5f1e9f3c.pdf",
  "created_at": "2026-07-05T14:19:05.762196Z",
  "status": "ready",
  "extracted_characters": 12500,
  "chunks_count": 15
}
```

При неправильном формате или превышении размера возвращается:

```text
400 Bad Request
```

## Список документов

Endpoint:

```text
GET /api/v1/documents
```

Пример:

```bash
curl http://localhost:8000/api/v1/documents
```

Ответ:

```json
{
  "documents": [
    {
      "id": 1,
      "uuid": "7ff85440-b40d-4fd7-9241-2f8c5f1e9f3c",
      "file_name": "lecture.pdf",
      "created_at": "2026-07-05T14:19:05.762196Z",
      "status": "ready"
    }
  ]
}
```

## Поиск

Endpoint:

```text
GET /api/v1/search?q={query}&page=1&page_size=10
```

Параметры:

| Параметр | Описание | Значение по умолчанию |
|---|---|---|
| `q` | поисковый запрос | обязательный |
| `page` | номер страницы | `1` |
| `page_size` | количество результатов на странице | `10` |

Пример:

```bash
curl "http://localhost:8000/api/v1/search?q=практика&page=1&page_size=10"
```

Ответ:

```json
{
  "query": "практика",
  "total": 25,
  "page": 1,
  "page_size": 10,
  "results": [
    {
      "chunk_id": "7ff85440-b40d-4fd7-9241-2f8c5f1e9f3c:1",
      "file_name": "lecture.pdf",
      "page": 2,
      "text": "фрагмент найденного текста",
      "score": 4.5
    }
  ]
}
```

## История поиска

После успешного поиска backend сохраняет запрос в PostgreSQL.

Endpoint:

```text
GET /api/v1/search/history
```

Пример:

```bash
curl http://localhost:8000/api/v1/search/history
```

Ответ:

```json
{
  "history": [
    {
      "query": "практика",
      "searched_at": "2026-07-05T14:22:10.123456Z",
      "results_count": 25
    }
  ]
}
```

## Проверка PostgreSQL

Список таблиц:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

Последние загруженные документы:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select id, uuid, file_name, status, created_at from documents order by id desc limit 10;"'
```

История поиска:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select query, results_count, searched_at from search_history order by searched_at desc limit 10;"'
```

## Проверка Elasticsearch

Health:

```bash
curl http://localhost:9200/_cluster/health
```

Mapping индекса:

```bash
curl http://localhost:9200/documents/_mapping
```

Количество проиндексированных чанков:

```bash
curl http://localhost:9200/documents/_count
```

## Проверка Redis

Проверка доступности:

```bash
docker compose exec redis redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

Ключи поискового кеша:

```bash
docker compose exec redis redis-cli keys "search:*"
```

TTL кеша задается переменной:

```env
SEARCH_CACHE_TTL_SECONDS=300
```

## Миграции

Миграции применяются автоматически при запуске backend-контейнера:

```bash
alembic upgrade head
```

Запуск вручную:

```bash
docker compose exec app alembic upgrade head
```

Текущие миграции создают:

- таблицу `documents`;
- поле `status` у документа;
- таблицу `search_history`.

## Метрики

Backend отдает метрики по адресу:

```text
http://localhost:8000/metrics
```

Основные метрики поиска:

```text
search_requests_total
search_response_duration_seconds_count
search_response_duration_seconds_sum
search_response_duration_seconds_bucket
```

Проверка:

```bash
curl http://localhost:8000/metrics
```

## Тесты

Запуск всех тестов:

```bash
python -m pytest
```

Запуск отдельных backend-тестов:

```bash
python -m pytest tests/test_document_upload.py
python -m pytest tests/test_search.py
python -m pytest tests/test_search_index.py
```

Ожидаемый результат:

```text
passed
```

## Частые проблемы

### Порт PostgreSQL занят

Если при запуске появляется ошибка:

```text
listen tcp 0.0.0.0:5432: bind: address already in use
```

измените внешний порт PostgreSQL в `.env`:

```env
POSTGRES_PORT=5433
```

### В базе не видно загруженный документ

Проверьте, к какой базе выполнено подключение. Если Docker публикует PostgreSQL на `5433`, то подключаться нужно так:

```text
host: localhost
port: 5433
database: knowledge_search
user: knowledge_user
password: knowledge_password
```

Проверка через контейнер:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "select * from documents;"'
```

### Elasticsearch не запускается

Проверьте, что в `.env` указана версия:

```env
ELASTIC_VERSION=9.4.2
```

Без этой переменной Docker не сможет собрать имя образа Elasticsearch.

## Остановка проекта

Остановить контейнеры:

```bash
docker compose down
```

Остановить и удалить volumes с данными:

```bash
docker compose down -v
```

Команда `docker compose down -v` удалит данные PostgreSQL, Elasticsearch и Redis.
