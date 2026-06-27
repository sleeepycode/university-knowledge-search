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

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || error.message || "Request failed");
  }
  return response.json();
}

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
