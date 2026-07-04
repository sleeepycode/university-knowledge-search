## Локальный запуск

### Backend

Требуется Python 3.12, доступный PostgreSQL, Elasticsearch и Redis.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
alembic upgrade head
curl http://localhost:9200
docker compose up -d redis
uvicorn backend.app.main:app --reload
```

Swagger доступен по адресу <http://127.0.0.1:8000/docs>.

### Реализовано

- FastAPI-приложение и `GET /api/v1/health`;
- `POST /api/v1/documents/upload`;
- валидация PDF/DOCX и лимита 20 МБ;
- сохранение файла с UUID в каталоге `uploads`;
- сохранение метаданных документа в PostgreSQL;
- миграция Alembic для таблицы `documents`;
- извлечение текста из PDF через `pdfplumber`;
- извлечение текста из DOCX через `python-docx`;
- разбиение текста на чанки по 1000 символов с перекрытием 100 символов;
- создание индекса `documents` в Elasticsearch;
- индексация чанков документа в Elasticsearch;
- `GET /api/v1/search?q=...` для поиска по чанкам документов;
- кеширование повторных поисковых запросов через Redis с TTL 5 минут.
