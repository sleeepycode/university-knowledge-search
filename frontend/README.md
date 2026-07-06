# 📚 Интеллектуальная поисковая система по базе знаний университета

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
- Email: [eastman19deni@gmail.com]
- GitHub: [https://github.com/sleeepycode/university-knowledge-search]