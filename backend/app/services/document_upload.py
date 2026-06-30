import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.document import Document

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
READ_CHUNK_SIZE = 1024 * 1024


async def validate_and_measure_file(
    file: UploadFile,
    max_size_bytes: int,
) -> int:
    file_name = file.filename or ""
    extension = Path(file_name).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are allowed",
        )

    size = 0
    while chunk := await file.read(READ_CHUNK_SIZE):
        size += len(chunk)
        if size > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="File size must not exceed 20 MB",
            )

    await file.seek(0)
    return size


async def save_document(
    file: UploadFile,
    upload_dir: Path,
    session: AsyncSession,
) -> Document:
    document_uuid = uuid.uuid4()
    extension = Path(file.filename or "").suffix.lower()
    destination = upload_dir / f"{document_uuid}{extension}"
    upload_dir.mkdir(parents=True, exist_ok=True)

    try:
        with destination.open("wb") as saved_file:
            while chunk := await file.read(READ_CHUNK_SIZE):
                saved_file.write(chunk)

        document = Document(
            uuid=document_uuid,
            file_name=file.filename or "",
            file_path=str(destination),
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document
    except Exception:
        await session.rollback()
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()


async def delete_saved_document(
    document: Document,
    session: AsyncSession,
) -> None:
    try:
        await session.delete(document)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        Path(document.file_path).unlink(missing_ok=True)
