import { useCallback, useRef, useState } from "react";
import type { Document } from "../api/client";
import { uploadDocument, HttpError } from "../api/client";
import { formatDate, getStatusLabel } from "../utils/highlight";
import { ErrorDisplay } from "./ErrorDisplay"; 

interface FileUploadProps {
  documents: Document[];
  onUploaded: () => void;
}

interface UploadItem {
  id: string;
  fileName: string;
  progress: number;
  status: Document["status"] | "uploading";
  error?: string;
}

export function FileUpload({ documents, onUploaded }: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploads, setUploads] = useState<UploadItem[]>([]);
  const [globalError, setGlobalError] = useState<Error | HttpError | string | null>(null); 

  const handleFiles = useCallback(
    async (files: FileList | File[]) => {
      setGlobalError(null); 
      
      const fileArray = Array.from(files).filter((file) => {
        const name = file.name.toLowerCase();
        return name.endsWith(".pdf") || name.endsWith(".docx");
      });


      if (fileArray.length === 0) {
        setGlobalError("Поддерживаются только файлы формата PDF и DOCX");
        return;
      }

      for (const file of fileArray) {
        const tempId = crypto.randomUUID();
        setUploads((prev) => [
          ...prev,
          {
            id: tempId,
            fileName: file.name,
            progress: 10,
            status: "uploading",
          },
        ]);

        try {
          setUploads((prev) =>
            prev.map((item) =>
              item.id === tempId ? { ...item, progress: 50, status: "uploaded" } : item,
            ),
          );

          const response = await uploadDocument(file);

          setUploads((prev) =>
            prev.map((item) =>
              item.id === tempId
                ? {
                    ...item,
                    id: response.document_id,
                    progress: 80,
                    status: "indexing",
                  }
                : item,
            ),
          );

          onUploaded();
        } catch (error) {
          let errorMessage = "Ошибка загрузки";

          if (error instanceof HttpError) {
            if (error.status === 400) {
              errorMessage = "Файл не прошел валидацию: " + error.message;
            } else if (error.status === 409) {
              errorMessage = "Такой документ уже существует: " + error.message;
            } else if (error.status === 413) {
              errorMessage = "Файл слишком большой. Максимальный размер: 20 МБ.";
            } else if (error.status === 415) {
              errorMessage = "Неподдерживаемый формат файла. Используйте PDF или DOCX.";
            } else if (error.status === 500) {
              errorMessage = "Ошибка сервера при обработке файла. Попробуйте позже.";
            } else {
              errorMessage = error.getUserMessage();
            }
          } else if (error instanceof Error) {
            errorMessage = error.message;
          }


          setGlobalError(errorMessage);

          setUploads((prev) =>
            prev.map((item) =>
              item.id === tempId
                ? {
                    ...item,
                    progress: 100,
                    status: "failed",
                    error: errorMessage,
                  }
                : item,
            ),
          );
        }
      }
    },
    [onUploaded],
  );

  const syncedUploads = uploads.map((item) => {
    const doc = documents.find((document) => document.document_id === item.id);
    if (!doc) {
      return item;
    }

    const progressByStatus: Record<Document["status"] | "uploading", number> = {
      uploading: 30,
      uploaded: 50,
      indexing: 80,
      ready: 100,
      failed: 100,
    };

    return {
      ...item,
      status: doc.status,
      progress: progressByStatus[doc.status],
    };
  });

  return (
    <section className="upload-section card">
      <h2>Загрузка документов</h2>
      

      {globalError && (
        <ErrorDisplay error={globalError} onRetry={() => setGlobalError(null)} />
      )}
      
      <div
        className={`dropzone ${dragOver ? "dropzone--active" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragOver(false);
          void handleFiles(event.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
      >
        <p className="dropzone__title">Перетащите PDF или DOCX сюда</p>
        <p className="dropzone__hint">или нажмите для выбора файлов</p>
        <button
          type="button"
          className="button button--secondary"
          onClick={(event) => {
            event.stopPropagation();
            inputRef.current?.click();
          }}
        >
          Выбрать файл
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          multiple
          hidden
          onChange={(event) => {
            if (event.target.files) {
              void handleFiles(event.target.files);
              event.target.value = "";
            }
          }}
        />
      </div>

      {syncedUploads.length > 0 && (
        <ul className="upload-list">
          {syncedUploads.map((item) => (
            <li key={item.id} className="upload-item">
              <div className="upload-item__header">
                <span>{item.fileName}</span>
                <span className={`status status--${item.status}`}>{getStatusLabel(item.status)}</span>
              </div>
              <div className="progress">
                <div
                  className={`progress__bar progress__bar--${item.status}`}
                  style={{ width: `${item.progress}%` }}
                />
              </div>

              {item.error && <p className="error-text">{item.error}</p>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

interface DocumentListProps {
  documents: Document[];
  loading: boolean;
}

export function DocumentList({ documents, loading }: DocumentListProps) {
  if (loading) {
    return <div className="card">Загрузка списка документов...</div>;
  }

  if (documents.length === 0) {
    return (
      <section className="card">
        <h2>Загруженные документы</h2>
        <p className="muted">Документы пока не загружены.</p>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Загруженные документы</h2>
      <ul className="document-list">
        {documents.map((doc) => (
          <li key={doc.document_id} className="document-item">
            <div>
              <strong>{doc.file_name}</strong>
              <p className="muted">{formatDate(doc.uploaded_at)}</p>
            </div>
            <span className={`status status--${doc.status}`}>{getStatusLabel(doc.status)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}