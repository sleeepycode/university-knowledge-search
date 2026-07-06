# University Knowledge Search

Веб-приложение для загрузки университетских документов, извлечения текста и полнотекстового поиска по учебным материалам.

## Архитектура

Проект запускается через Docker Compose и включает следующие сервисы:

| Сервис | Назначение | Адрес |
|---|---|---|
| `front` | React frontend и Nginx | `http://localhost:3000` |
| `app` | FastAPI backend | `http://localhost:8000` |
| `postgres` | Метаданные документов | `localhost:5432` |
| `elasticsearch` | Полнотекстовый поиск | `http://localhost:9200` |
| `redis` | Кеширование | `localhost:6379` |
| `prometheus` | Сбор метрик | `http://localhost:9090` |
| `grafana` | Отображение метрик | `http://localhost:3001` |

## Требования

Для запуска необходимы:

- Git;
- Docker Desktop;
- Docker Compose;
- Git Bash для запуска `init.sh`.

Устанавливать Python, Node.js, npm или Bun локально не требуется.

## Клонирование репозитория

```bash
git clone https://github.com/sleeepycode/university-knowledge-search.git
cd university-knowledge-search
```

Для работы с интеграционной версией:

```bash
git switch dev
git pull
```

## Настройка окружения

Скопируйте пример переменных окружения.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Linux, macOS или Git Bash

```bash
cp .env.example .env
```

Перед публичным развёртыванием измените стандартные пароли в `.env`.

Файл `.env` содержит локальные настройки и не должен добавляться в Git.

## Запуск проекта

Запустите Docker Desktop.

Затем выполните:

```bash
docker compose up --build -d
```

Проверка состояния контейнеров:

```bash
docker compose ps
```

Ожидаемые сервисы:

```text
postgres
elasticsearch
redis
app
front
prometheus
grafana
```

## Проверка backend

Health endpoint:

```text
http://localhost:8000/api/v1/health
```

Проверка через PowerShell:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/health"
```

Swagger:

```text
http://localhost:8000/docs
```

Backend через Nginx:

```text
http://localhost:3000/api/v1/health
```

## Загрузка документа

API endpoint:

```text
POST /api/v1/documents/upload
```

Пример через curl:

```bash
curl \
  --request POST \
  --form "file=@document.pdf" \
  http://localhost:8000/api/v1/documents/upload
```

Поддерживаемые форматы:

- PDF;
- DOCX.

Максимальный размер одного документа — 20 МБ.

## Начальное наполнение

Скрипт `init.sh`:

1. ожидает готовности backend;
2. скачивает 10 открытых PDF-лекций MIT OpenCourseWare;
3. проверяет, что скачанные файлы являются PDF;
4. отправляет каждый документ в API;
5. выводит итоговое количество успешных загрузок;
6. удаляет временные файлы после завершения.

Сначала запустите проект:

```bash
docker compose up --build -d
```

Затем откройте Git Bash и выполните:

```bash
bash init.sh
```

Для другого адреса API:

```bash
API_URL=http://example.com/api/v1 bash init.sh
```

Успешный результат:

```text
Всего документов: 10
Скачано: 10
Загружено: 10
Ошибок: 0
Все 10 PDF успешно загружены.
```

## Проверка PostgreSQL

Проверка таблиц:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\dt"'
```

Количество сохранённых документов:

```bash
docker compose exec postgres \
  sh -lc 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) FROM documents;"'
```

## Проверка Redis

```bash
docker compose exec redis redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

## Prometheus

Интерфейс Prometheus:

```text
http://localhost:9090
```

Проверка цели backend:

```text
Status → Target health
```

Ожидаемое состояние:

```text
backend — UP
```

Backend отдаёт метрики по адресу:

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

## Grafana

Интерфейс Grafana:

```text
http://localhost:3001
```

Стандартные данные локального окружения:

```text
Логин: admin
Пароль: change_me
```

Пароль задаётся переменной:

```text
GRAFANA_ADMIN_PASSWORD
```

Dashboard:

```text
Dashboards
→ University Knowledge Search
→ Search API Monitoring
```

Панели:

- `Search requests total`;
- `Average search response time`.

## Backend-тесты

Backend-проверки выполняются автоматически через GitHub Actions.

Локальный запуск через Docker:

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -w /workspace \
  python:3.12-slim \
  sh -c "pip install -r requirements-dev.txt ruff && ruff check backend tests && python -m pytest"
```

## Frontend-проверки

```bash
docker run --rm \
  -v "$(pwd):/workspace" \
  -w /workspace/frontend \
  oven/bun:1-alpine \
  sh -c "bun install --frozen-lockfile && bunx oxlint@1.72.0 src && bun run test && bun run build"
```

## GitHub Actions

Workflow находится в:

```text
.github/workflows/ci.yml
```

CI выполняет:

1. Ruff для backend;
2. pytest для backend;
3. Oxlint для frontend;
4. frontend-тесты;
5. TypeScript/Vite build;
6. проверку Docker Compose;
7. сборку образов `app` и `front`.

Workflow запускается для Pull Request в `dev` и `main`, а также при push в `main`.

## Просмотр логов

Все сервисы:

```bash
docker compose logs --tail=200
```

Backend:

```bash
docker compose logs app --tail=200
```

Frontend:

```bash
docker compose logs front --tail=200
```

PostgreSQL:

```bash
docker compose logs postgres --tail=200
```

Elasticsearch:

```bash
docker compose logs elasticsearch --tail=200
```

Redis:

```bash
docker compose logs redis --tail=200
```

Prometheus:

```bash
docker compose logs prometheus --tail=200
```

Grafana:

```bash
docker compose logs grafana --tail=200
```

Для просмотра логов в реальном времени:

```bash
docker compose logs -f app
```

## Остановка проекта

```bash
docker compose down
```

Эта команда останавливает контейнеры, но сохраняет данные в Docker volumes.

## Полная очистка

```bash
docker compose down -v --remove-orphans
```

Внимание: команда удаляет:

- базу PostgreSQL;
- индекс Elasticsearch;
- Redis-данные;
- загруженные документы;
- историю Prometheus;
- локальные данные Grafana.

## Повторная сборка

```bash
docker compose up --build -d
```

Сборка без Docker cache:

```bash
docker compose build --no-cache app front
docker compose up -d
```

## Типичные ошибки

### Docker Desktop не запущен

Проверьте:

```bash
docker version
```

В выводе должны присутствовать разделы `Client` и `Server`.

### Порт уже занят

Измените соответствующий порт в локальном `.env`.

### Backend не запускается

```bash
docker compose logs app --tail=200
```

### Elasticsearch не запускается

Проверьте выделенную Docker Desktop оперативную память. Для полного стека рекомендуется не менее 4 ГБ.

### PostgreSQL сообщает об ошибке пароля

Для чистого локального окружения:

```bash
docker compose down -v
docker compose up --build -d
```

Команда удалит старую локальную базу.

### Grafana не принимает пароль

Переменные администратора применяются при первоначальном создании Grafana volume. При необходимости удалите только локальный Grafana volume либо выполните полный сброс окружения.

### `init.sh` сообщает, что backend недоступен

Проверьте:

```bash
docker compose ps
docker compose logs app --tail=200
```

Health endpoint должен отвечать:

```text
http://localhost:8000/api/v1/health
```

### `init.sh` сообщает об ошибке загрузки

Проверьте:

```bash
docker compose logs app --tail=200
```

Также убедитесь, что endpoint загрузки доступен в Swagger:

```text
http://localhost:8000/docs
```
# QA-инженер 

## Технологический стек

| Назначение | Инструмент |
|------------|------------|
| Юнит-тесты | `pytest`, `pytest-cov` |
| E2E-тесты | `Playwright` |
| Нагрузочные тесты | `locust` |
| Работа с API | `requests` / `httpx` |
| Документация | PDF |
---

##  Виды тестирования

### 1. Юнит-тесты (QA-01)
 **Команда:** `pytest --cov=backend --cov-report=term-missing --cov-report=xml --cov-fail-under=50`

### 2. E2E-тесты (QA-02)
**Запуск:** `pytest tests/e2e/test_document_flow.py --headed -v -s`

##  Итоговые артефакты QA

- [ ] Юнит-тесты (`tests/`)
- [ ] E2E-тесты (`tests/e2e/`)
- [ ] Тестовые данные (`tests/e2e/fixtures/`)
- [ ] Нагрузочные тесты (`tests/locust_load/`)
- [ ] Руководство пользователя (`USER_GUIDE.pdf`)



---


> **Frontend-часть** веб-приложения для загрузки документов и полнотекстового поиска по внутренней базе знаний.

---

## 📋 О проекте

Интеллектуальная поисковая система предназначена для организации и быстрого поиска информации по документам университета. Система позволяет загружать документы в форматах **PDF** и **DOCX**, автоматически обрабатывать их и выполнять полнотекстовый поиск с подсветкой совпадений и ранжированием результатов.

### Основные возможности
- ✅ Загрузка документов через **Drag-and-Drop**
- ✅ Отображение статуса обработки документов (Загрузка → Индексация → Готово)
- ✅ Полнотекстовый поиск по всем загруженным документам
- ✅ Подсветка найденных слов в результатах
- ✅ Пагинация результатов поиска
- ✅ Адаптивный дизайн для всех устройств
- ✅ Интеграция с backend API

---

## 🛠 Технологический стек

### Frontend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **React** | 18.x | Библиотека для построения пользовательского интерфейса |
| **TypeScript** | 5.x | Типизация и улучшение качества кода |
| **Vite** | 5.x | Инструмент сборки и разработки |
| **React Router** | 6.x | Маршрутизация между страницами |
| **Axios** | 1.x | HTTP-клиент для взаимодействия с API |
| **SCSS** | - | Препроцессор для стилизации |
| **Vitest** | 2.x | Фреймворк для юнит-тестирования |

### Backend (внешний API)

| Технология | Назначение |
|------------|------------|
| **FastAPI** | Фреймворк для REST API |
| **PostgreSQL** | Основная база данных |
| **Elasticsearch** | Полнотекстовый поиск и индексация |
| **Redis** | Кеширование поисковых запросов |
| **Docker / Docker Compose** | Контейнеризация и оркестрация |

---

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── api/                    # API-клиенты
│   │   ├── client.ts           # Настройка Axios
│   │   ├── documents.ts        # Запросы для работы с документами
│   │   └── search.ts           # Запросы для поиска
│   │
│   ├── components/             # Переиспользуемые компоненты
│   │   ├── Layout/             # Обертка приложения (шапка, навигация)
│   │   ├── FileUpload/         # Загрузка файлов с Drag-and-Drop
│   │   ├── DocumentList/       # Список документов со статусами
│   │   ├── SearchResults/      # Карточки результатов поиска
│   │   └── Pagination/         # Компонент пагинации
│   │
│   ├── pages/                  # Страницы приложения
│   │   ├── HomePage/           # Главная страница (загрузка)
│   │   └── SearchPage/         # Страница поиска
│   │
│   ├── styles/                 # Стили
│   │   ├── variables.scss      # SCSS-переменные
│   │   └── global.scss         # Глобальные стили
│   │
│   ├── types/                  # TypeScript-интерфейсы
│   │   ├── document.ts         # Типы для документов
│   │   └── search.ts           # Типы для поиска
│   │
│   ├── utils/                  # Вспомогательные функции
│   │   ├── highlight.ts        # Подсветка совпадений
│   │   └── status.ts           # Работа со статусами
│   │
│   ├── App.tsx                 # Корневой компонент
│   ├── main.tsx                # Точка входа
│   └── vite-env.d.ts           # Типы для Vite
│
├── public/                     # Статические файлы
├── index.html                  # HTML-шаблон
├── package.json                # Зависимости и скрипты
├── tsconfig.json               # Настройки TypeScript
├── vite.config.ts              # Настройки Vite
└── README.md                   # Документация проекта
```

---

## 🚀 Запуск проекта

### Требования
- **Node.js** версии 18 или выше
- **npm** или **yarn**

### Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/your-username/knowledge-search.git
cd knowledge-search/frontend

# 2. Установить зависимости
bun install

# 3. Создать файл .env (скопировать из .env.example)
cp .env.example .env

# 4. Запустить в режиме разработки
bun run dev

# 5. Открыть в браузере
# http://localhost:3000
```

### Доступные скрипты

| Команда | Описание |
|---------|----------|
| `bun run dev` | Запуск в режиме разработки |
| `bun run build` | Сборка production версии |
| `bun run preview` | Просмотр собранного приложения |
| `bun run test` | Запуск юнит-тестов |
| `bun run lint` | Проверка кода линтером |

---

## 🔧 Конфигурация

### Переменные окружения (.env)

```env
# API
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Настройки приложения
VITE_APP_TITLE=Поиск по базе знаний
VITE_POLLING_INTERVAL=5000  # Интервал обновления статусов (мс)
VITE_PAGE_SIZE=10           # Количество результатов на странице
```

### TypeScript

Проект использует строгую типизацию. Все интерфейсы описаны в папке `src/types/`.

```typescript

interface Document {
  id: number;
  uuid: string;
  file_name: string;
  status: 'uploading' | 'processing' | 'ready' | 'error';
  created_at: string;
  chunks_count?: number;
}


interface SearchResult {
  chunk_id: string;
  file_name: string;
  page: number;
  text: string;
  score: number;
}
```

---

## 🧪 Тестирование

Юнит-тесты написаны с использованием **Vitest**. Основные тестируемые функции:

- `highlightText()` — проверка корректности подсветки совпадений
- `getStatusLabel()` — проверка отображения статусов

```bash
# Запуск всех тестов
bun run test

# Запуск с покрытием
bun run test -- --coverage
```

---

## 📦 Взаимодействие с API

### Эндпоинты backend

| Метод | URL | Описание |
|-------|-----|----------|
| `POST` | `/documents/upload` | Загрузка документа |
| `GET` | `/documents` | Получение списка документов |
| `GET` | `/search?q={query}&page={page}&page_size={size}` | Полнотекстовый поиск |
| `GET` | `/search/history` | История поисковых запросов |

### Пример запроса на поиск

```typescript
// src/api/search.ts
import { apiClient } from './client';

export const searchDocuments = (query: string, page: number = 1, pageSize: number = 10) => {
  return apiClient.get('/search', {
    params: { q: query, page, page_size: pageSize }
  });
};
```

---

## 🎨 Особенности реализации

### Подсветка совпадений (Highlight)

Функция `highlightText` находит все вхождения слов из запроса в тексте и обертывает их в тег `<mark>`:

```typescript
// src/utils/highlight.ts
export function highlightText(text: string, query: string): string {

  const words = query.split(/\s+/).filter(Boolean);

  const regex = new RegExp(`(${words.map(w => escapeRegex(w)).join('|')})`, 'gi');

  return escapeHtml(text).replace(regex, '<mark>$1</mark>');
}
```

### Отслеживание статусов (Polling)

Для обновления статусов документов используется механизм polling:

```typescript
// Компонент DocumentList
useEffect(() => {
  const interval = setInterval(() => {
    fetchDocuments();
  }, 5000); 
  
  return () => clearInterval(interval);
}, []);
```

---

## 🌐 Адаптивность

Проект адаптирован для следующих разрешений экрана:

| Устройство | Разрешение |
|------------|------------|
| Мобильные телефоны | 320px - 767px |
| Планшеты | 768px - 1023px |
| Ноутбуки | 1024px - 1439px |
| Десктопы | 1440px+ |

Медиа-запросы настроены в файлах SCSS для каждого компонента.

---

## 📝 Лицензия

Проект разработан в рамках учебной практики в МТУСИ.

---

## 👥 Команда

| Роль | Имя | Группа |
|------|-----|--------|
| Frontend-разработчик | Ганятов Даниял | БПИ2404 |
| QA-разработчик | Халимон Иван | БПИ2404 |
| DevOps-разработчик | Сидельников Николай | БПИ2404|
| Backend-разработчик | Капранов Владимир Сергеевич | БПИ2404 |
| Руководитель практики | Мосева М.С. | Доцент каф. ПИ |

---

## 📧 Контакты

По вопросам, связанным с проектом, обращайтесь:
- GitHub: [https://github.com/sleeepycode/university-knowledge-search]
