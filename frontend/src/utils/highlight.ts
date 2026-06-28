export function highlightQuery(text: string, query: string): string {
  if (!query.trim()) {
    return escapeHtml(text);
  }

  const words = query
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));

  if (words.length === 0) {
    return escapeHtml(text);
  }

  const pattern = new RegExp(`(${words.join("|")})`, "gi");
  const parts = text.split(pattern);

  return parts
    .map((part, index) => {
      const escaped = escapeHtml(part);
      if (index % 2 === 1) {
        return `<mark class="highlight">${escaped}</mark>`;
      }
      return escaped;
    })
    .join("");
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

export function getStatusLabel(status: string): string {
const labels: Record<string, string> = {
  uploading: "Загрузка...",  
  uploaded: "Загружено",     
  indexing: "Индексация...",
  ready: "Готово",
  failed: "Ошибка",
};

  return labels[status] || status;
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
