import { FormEvent, useEffect, useState } from "react";
import type { SearchHistoryItem, SearchResponse } from "../api/client";
import { fetchSearchHistory, searchDocuments } from "../api/client";
import { Pagination, SearchResultCard } from "../components/SearchResult";

const PAGE_SIZE = 10;

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [page, setPage] = useState(1);
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);

  useEffect(() => {
    void fetchSearchHistory()
      .then(setHistory)
      .catch(() => setHistory([]));
  }, []);

  useEffect(() => {
    if (!submittedQuery.trim()) {
      return;
    }

    const runSearch = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await searchDocuments(submittedQuery, page, PAGE_SIZE);
        setResults(data);
        const historyData = await fetchSearchHistory();
        setHistory(historyData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Ошибка поиска");
        setResults(null);
      } finally {
        setLoading(false);
      }
    };

    void runSearch();
  }, [submittedQuery, page]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    setPage(1);
    setSubmittedQuery(query.trim());
  };

  return (
    <div className="page">
      <h1>Поиск по документам</h1>

      <form className="search-form card" onSubmit={handleSubmit}>
        <label htmlFor="search-input" className="search-form__label">
          Поисковый запрос
        </label>
        <div className="search-form__row">
          <input
            id="search-input"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Например: python"
            className="search-form__input"
          />
          <button type="submit" className="button">
            Найти
          </button>
        </div>
      </form>

      {history.length > 0 && (
        <section className="card history">
          <h2>История поиска</h2>
          <ul className="history__list">
            {history.map((item, index) => (
              <li key={`${item.query}-${item.searched_at}-${index}`}>
                <button
                  type="button"
                  className="history__item"
                  onClick={() => {
                    setQuery(item.query);
                    setSubmittedQuery(item.query);
                    setPage(1);
                  }}
                >
                  {item.query}
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {loading && <div className="card">Поиск...</div>}
      {error && <div className="card error-text">{error}</div>}

      {!loading && submittedQuery && results && results.total === 0 && (
        <div className="card empty-state">
          По вашему запросу ничего не найдено. Попробуйте изменить формулировку
        </div>
      )}

      {!loading && results && results.results.length > 0 && (
        <>
          <p className="results-meta">
            Найдено: {results.total}. Страница {results.page} из{" "}
            {Math.max(1, Math.ceil(results.total / PAGE_SIZE))}
          </p>
          <div className="results-list">
            {results.results.map((result) => (
              <SearchResultCard key={result.chunk_id} result={result} query={submittedQuery} />
            ))}
          </div>
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            total={results.total}
            onPageChange={setPage}
          />
        </>
      )}
    </div>
  );
}
