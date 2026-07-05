from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

import pdfplumber
from docx import Document as DocxDocument


class UnsupportedDocumentTypeError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    page_number: int
    text: str


def extract_text(file: BinaryIO, file_name: str) -> str:
    return "\n\n".join(page.text for page in extract_pages(file, file_name))


def extract_pages(file: BinaryIO, file_name: str) -> list[ExtractedPage]:
    extension = Path(file_name).suffix.lower()

    if extension == ".pdf":
        return extract_pdf_pages(file)
    if extension == ".docx":
        return extract_docx_pages(file)

    raise UnsupportedDocumentTypeError(
        f"Unsupported document extension: {extension}"
    )


def extract_pdf_pages(file: BinaryIO) -> list[ExtractedPage]:
    with pdfplumber.open(file) as pdf:
        return [
            ExtractedPage(page_number=page_number, text=text.strip())
            for page_number, page in enumerate(pdf.pages, start=1)
            if (text := page.extract_text())
        ]


def extract_pdf_text(file: BinaryIO) -> str:
    return "\n\n".join(page.text for page in extract_pdf_pages(file))


def extract_docx_pages(file: BinaryIO) -> list[ExtractedPage]:
    text = extract_docx_text(file)
    if not text:
        return []
    return [ExtractedPage(page_number=1, text=text)]


def extract_docx_text(file: BinaryIO) -> str:
    document = DocxDocument(file)
    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n\n".join(paragraphs)
