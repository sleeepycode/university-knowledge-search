import type { SearchResult } from "../api/client";
import { highlightQuery } from "../utils/highlight";

interface SearchResultCardProps {
  result: SearchResult;
  query: string;
}

export function SearchResultCard({ result, query }: SearchResultCardProps) {
  return (
    <article className="result-card">
      <header className="result-card__header">
        <h3>{result.file_name}</h3>
        <span className="result-card__score">Score: {result.score.toFixed(2)}</span>
      </header>
      <p className="result-card__meta">Страница {result.page}</p>
      <div
        className="result-card__text"
        dangerouslySetInnerHTML={{ __html: highlightQuery(result.text, query) }}
      />
    </article>
  );
}

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, pageSize, total, onPageChange }: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  if (totalPages <= 1) {
    return null;
  }

  const pages = Array.from({ length: totalPages }, (_, index) => index + 1).slice(
    Math.max(0, page - 3),
    Math.max(0, page - 3) + 5,
  );

  return (
    <nav className="pagination" aria-label="Пагинация результатов">
      <button
        type="button"
        className="button button--secondary"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        Назад
      </button>
      <div className="pagination__pages">
        {pages.map((pageNumber) => (
          <button
            key={pageNumber}
            type="button"
            className={`pagination__page ${pageNumber === page ? "active" : ""}`}
            onClick={() => onPageChange(pageNumber)}
          >
            {pageNumber}
          </button>
        ))}
      </div>
      <button
        type="button"
        className="button button--secondary"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Вперёд
      </button>
    </nav>
  );
}
