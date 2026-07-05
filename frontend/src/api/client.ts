// --- Интерфейсы согласно реальному контракту бэкенда ---

export interface Document {
  id: number;
  uuid: string;
  file_name: string;
  created_at: string;
  status: "ready";
}

export interface UploadResponse {
  id: number;
  uuid: string;
  file_name: string;
  file_path: string;
  created_at: string;
  status: string;
  extracted_characters: number;
  chunks_count: number;
}

// SearchResult - результаты поиска по чанкам
export interface SearchResult {
  chunk_id: string;
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

    if (response.ok) {
      if (response.status === 204) {
        return null as T;
      }
      return response.json();
    }

    let errorData: any = {};
    let errorMessage = "Request failed";

    try {
      errorData = await response.json();
      errorMessage = errorData.detail || errorData.message || errorData.error || "Request failed";
    } catch {
      errorMessage = response.statusText || `HTTP ${response.status}`;
    }

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
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      throw new HttpError(
        0,
        "Не удалось подключиться к серверу. Проверьте ваше интернет-соединение.",
        "Network error",
      );
    }

    if (error instanceof HttpError) {
      throw error;
    }

    throw new HttpError(
      500,
      error instanceof Error ? error.message : "Неизвестная ошибка",
    );
  }
}

// --- API-функции ---

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

// Удален fetchDocument - нет такого эндпоинта в бэкенде

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

