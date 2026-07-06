from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.db.session import get_db_session
from backend.app.models.document import Document
from backend.app.schemas.document import (
    DocumentListItem,
    DocumentListResponse,
    DocumentUploadResponse,
)
from backend.app.services.document_processing import process_document
from backend.app.services.document_upload import (
    delete_saved_document,
    save_document,
    validate_and_measure_file,
)
from backend.app.services.search_index import (
    SearchIndexUnavailableError,
    index_document_chunks,
    search_index_error,
)

router = APIRouter()
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("", response_model=DocumentListResponse)
async def list_documents(session: DatabaseSession) -> DocumentListResponse:
    result = await session.execute(
        select(Document).order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[
            DocumentListItem(
                id=document.id,
                uuid=document.uuid,
                file_name=document.file_name,
                created_at=document.created_at,
                status=document.status,
            )
            for document in documents
        ]
    )


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    session: DatabaseSession,
    file: UploadFile = File(description="PDF or DOCX document, up to 20 MB"),
) -> DocumentUploadResponse:
    await validate_and_measure_file(
        file=file,
        max_size_bytes=settings.max_upload_size_bytes,
    )
    processing_result = await process_document(
        file=file,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    document = await save_document(
        file=file,
        upload_dir=settings.upload_dir,
        session=session,
    )
    try:
        await index_document_chunks(document, processing_result.chunks)
    except SearchIndexUnavailableError as error:
        await delete_saved_document(document, session)
        raise search_index_error() from error

    return DocumentUploadResponse(
        id=document.id,
        uuid=document.uuid,
        file_name=document.file_name,
        file_path=document.file_path,
        created_at=document.created_at,
        status=document.status,
        extracted_characters=len(processing_result.text),
        chunks_count=len(processing_result.chunks),
    )
