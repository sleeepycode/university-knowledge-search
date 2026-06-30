export interface Document {
  document_id: string;
  file_name: string;
  uploaded_at: string;
  status: "uploaded" | "indexing" | "ready" | "failed";
  chunks_count?: number;
}

export interface UploadResponse {
  document_id: string;
  file_name: string;
  status: string;
  message: string;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  file_name: string;
  page: number;
  text: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  total: number;
  page: number;
  page_size: number;
  results: SearchResult[];
}

export interface SearchHistoryItem {
  query: string;
  searched_at: string;
  results_count: number;
}

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
  errors?: Record<string, string[]>;
}

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

// --- Кастомный класс ошибки с HTTP-статусом ---
export class HttpError extends Error {
  public readonly status: number;
  public readonly detail?: string;
  public readonly errors?: Record<string, string[]>;

  constructor(status: number, message: string, detail?: string, errors?: Record<string, string[]>) {
    super(message);
    this.name = "HttpError";
    this.status = status;
    this.detail = detail;
    this.errors = errors;
    Object.setPrototypeOf(this, HttpError.prototype);
  }

  // Вспомогательные методы для проверки статуса
  isNotFound(): boolean {
    return this.status === 404;
  }

  isUnauthorized(): boolean {
    return this.status === 401;
  }

  isForbidden(): boolean {
    return this.status === 403;
  }

  isBadRequest(): boolean {
    return this.status === 400;
  }

  isServerError(): boolean {
    return this.status >= 500;
  }

  isConflict(): boolean {
    return this.status === 409;
  }

  // Человекочитаемое описание ошибки
  getUserMessage(): string {
    const messages: Record<number, string> = {
      400: "Неверный запрос. Проверьте введенные данные.",
      401: "Требуется авторизация. Пожалуйста, войдите в систему.",
      403: "Доступ запрещен. У вас недостаточно прав.",
      404: "Запрашиваемый ресурс не найден.",
      409: "Конфликт данных. Возможно, такой документ уже существует.",
      422: "Ошибка валидации данных.",
      429: "Слишком много запросов. Попробуйте позже.",
      500: "Внутренняя ошибка сервера. Попробуйте позже.",
      502: "Сервер временно недоступен.",
      503: "Сервис временно недоступен.",
    };

    if (this.status in messages) {
      return messages[this.status as keyof typeof messages];
    }

    return this.message || "Произошла неизвестная ошибка.";
  }
}

// --- Основная функция запроса с детальной обработкой ---
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`, options);

    // Обработка успешного ответа (2xx)
    if (response.ok) {
      // Для 204 No Content возвращаем null
      if (response.status === 204) {
        return null as T;
      }
      return response.json();
    }

    // --- Обработка ошибок по HTTP-статусам ---
    let errorData: any = {};
    let errorMessage = "Request failed";

    try {
      errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorData.error || "Request failed";
    } catch {
      // Если тело ответа не JSON
      errorMessage = response.statusText || `HTTP ${response.status}`;
    }

    // Формируем осмысленное сообщение в зависимости от статуса
    let userMessage = errorMessage;
    switch (response.status) {
      case 400:
        userMessage = "Ошибка валидации данных. Проверьте правильность заполнения формы.";
        break;
      case 401:
        userMessage = "Требуется авторизация. Пожалуйста, войдите в систему.";
        break;
      case 403:
        userMessage = "Доступ запрещен. У вас недостаточно прав для выполнения этого действия.";
        break;
      case 404:
        userMessage = "Запрашиваемый ресурс не найден. Возможно, он был удален.";
        break;
      case 409:
        userMessage = "Конфликт данных. Возможно, такой документ уже существует.";
        break;
      case 422:
        userMessage = "Ошибка валидации. Проверьте введенные данные.";
        break;
      case 429:
        userMessage = "Слишком много запросов. Пожалуйста, подождите и попробуйте снова.";
        break;
      case 500:
      case 502:
      case 503:
        userMessage = "Внутренняя ошибка сервера. Попробуйте позже.";
        break;
      default:
        userMessage = errorMessage || `Ошибка ${response.status}: ${response.statusText}`;
    }

    throw new HttpError(
      response.status,
      userMessage,
      errorData.detail || errorData.message,
      errorData.errors,
    );
  } catch (error) {
    // Перехватываем сетевые ошибки (нет соединения с сервером)
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new HttpError(
        0,
        "Не удалось подключиться к серверу. Проверьте ваше интернет-соединение.",
        "Network error",
      );
    }

    // Если ошибка уже HttpError — пробрасываем дальше
    if (error instanceof HttpError) {
      throw error;
    }

    // Любые другие ошибки
    throw new HttpError(
      500,
      error instanceof Error ? error.message : "Неизвестная ошибка",
    );
  }
}

// --- API-функции с обработкой ошибок ---

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function fetchDocuments(): Promise<Document[]> {
  const data = await request<{ documents: Document[] }>("/documents");
  return data.documents;
}

export async function fetchDocument(documentId: string): Promise<Document> {
  return request<Document>(`/documents/${documentId}`);
}

export async function searchDocuments(
  query: string,
  page = 1,
  pageSize = 10,
): Promise<SearchResponse> {
  const params = new URLSearchParams({
    q: query,
    page: String(page),
    page_size: String(pageSize),
  });
  return request<SearchResponse>(`/search?${params.toString()}`);
}

export async function fetchSearchHistory(): Promise<SearchHistoryItem[]> {
  const data = await request<{ history: SearchHistoryItem[] }>("/search/history");
  return data.history;
}