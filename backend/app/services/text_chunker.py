from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TextChunk:
    chunk_number: int
    page_number: int
    text: str


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero")
    if overlap < 0:
        raise ValueError("Chunk overlap must not be negative")
    if overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size")

    normalized_text = text.strip()
    if not normalized_text:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    start = 0

    while start < len(normalized_text):
        end = min(start + chunk_size, len(normalized_text))
        chunks.append(normalized_text[start:end])

        if end == len(normalized_text):
            break
        start += step

    return chunks


def split_pages_into_chunks(
    pages: list[tuple[int, str]],
    chunk_size: int = 1000,
    overlap: int = 100,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []

    for page_number, page_text in pages:
        for chunk_text in split_text_into_chunks(
            text=page_text,
            chunk_size=chunk_size,
            overlap=overlap,
        ):
            chunks.append(
                TextChunk(
                    chunk_number=len(chunks) + 1,
                    page_number=page_number,
                    text=chunk_text,
                )
            )

    return chunks
