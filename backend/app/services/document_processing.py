from dataclasses import dataclass

from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from backend.app.services.document_parser import extract_pages
from backend.app.services.text_chunker import TextChunk, split_pages_into_chunks


@dataclass(frozen=True, slots=True)
class ProcessingResult:
    text: str
    chunks: list[TextChunk]


async def process_document(
    file: UploadFile,
    chunk_size: int,
    chunk_overlap: int,
) -> ProcessingResult:
    try:
        await file.seek(0)
        pages = await run_in_threadpool(
            extract_pages,
            file.file,
            file.filename or "",
        )
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Could not extract text from the document",
        ) from error
    finally:
        await file.seek(0)

    text = "\n\n".join(page.text for page in pages)
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="The document does not contain extractable text",
        )

    chunks = split_pages_into_chunks(
        pages=[(page.page_number, page.text) for page in pages],
        chunk_size=chunk_size,
        overlap=chunk_overlap,
    )
    return ProcessingResult(text=text, chunks=chunks)
