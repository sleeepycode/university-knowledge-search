
import { useCallback, useEffect, useState } from "react";
import type { Document } from "../api/client";
import { fetchDocument, fetchDocuments, HttpError } from "../api/client";
import { DocumentList, FileUpload } from "../components/FileUpload";
import { ErrorDisplay } from "../components/ErrorDisplay"; 

export default function HomePage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | HttpError | string | null>(null); 

  const loadDocuments = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch (err) {
      setError(err instanceof Error ? err : "Ошибка загрузки документов");
      setDocuments([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDocuments();
  }, [loadDocuments]);

  useEffect(() => {
    const interval = setInterval(async () => {
      const pending = documents.filter(
        (doc) => doc.status === "uploaded" || doc.status === "indexing",
      );
      if (pending.length === 0) {
        return;
      }

      const updated = await Promise.all(
        pending.map(async (doc) => {
          try {
            return await fetchDocument(doc.document_id);
          } catch {
            return doc;
          }
        }),
      );

      setDocuments((prev) =>
        prev.map((doc) => {
          const refreshed = updated.find((item) => item.document_id === doc.document_id);
          return refreshed || doc;
        }),
      );
    }, 3000);

    return () => clearInterval(interval);
  }, [documents]);

  return (
    <div className="page">
      <h1>Главная страница</h1>
      <p className="page__subtitle">Загрузите PDF или DOCX для полнотекстового поиска</p>
      

      {error && <ErrorDisplay error={error} onRetry={loadDocuments} />}
      
      <FileUpload documents={documents} onUploaded={loadDocuments} />
      <DocumentList documents={documents} loading={loading} />
    </div>
  );
}