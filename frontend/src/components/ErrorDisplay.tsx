
import { HttpError } from "../api/client";

interface ErrorDisplayProps {
  error: Error | HttpError | string | null;
  onRetry?: () => void;
}

export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  if (!error) return null;

  let message: string;
  let status: number | undefined;
  let isHttpError = false;

  if (typeof error === "string") {
    message = error;
  } else if (error instanceof HttpError) {
    message = error.getUserMessage();
    status = error.status;
    isHttpError = true;
  } else {
    message = error.message || "Произошла ошибка";
  }

  const getStatusIcon = () => {
    if (!status) return "⚠️";
    if (status >= 500) return "🔥";
    if (status === 404) return "🔍";
    if (status === 401 || status === 403) return "🔒";
    if (status === 400 || status === 422) return "✏️";
    if (status === 429) return "⏳";
    return "⚠️";
  };

  const getStatusClass = () => {
    if (!status) return "error";
    if (status >= 500) return "error error--server";
    if (status === 404) return "error error--notfound";
    if (status === 401 || status === 403) return "error error--auth";
    if (status === 400 || status === 422) return "error error--validation";
    return "error";
  };

  return (
    <div className={`error-card ${getStatusClass()}`}>
      <div className="error-card__icon">{getStatusIcon()}</div>
      <div className="error-card__content">
        {status && <span className="error-card__status">Ошибка {status}</span>}
        <p className="error-card__message">{message}</p>
        {isHttpError && error instanceof HttpError && error.detail && (
          <p className="error-card__detail">{error.detail}</p>
        )}
        {onRetry && (
          <button type="button" className="button button--secondary" onClick={onRetry}>
            Попробовать снова
          </button>
        )}
      </div>
    </div>
  );
}