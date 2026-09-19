"""Text chunker with sliding window, overlap, and provenance metadata."""

from dataclasses import dataclass
from typing import Optional

from app.ingestion.extractors.base_extractor import ExtractedDocument
from app.ingestion.normalizer import normalize_text
from app.utils.logging import get_logger

logger = get_logger("ingestion.chunker")


@dataclass
class ChunkData:
    """Dataclass holding chunk content and provenance for DB insertion."""
    chunk_index: int
    content: str
    clean_content: str
    start_char: int
    end_char: int
    page_number: Optional[int]
    section_header: Optional[str]
    token_count: int


class TextChunker:
    """Sliding window chunker with overlapping boundaries and provenance tracking."""

    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 400):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: ExtractedDocument) -> list[ChunkData]:
        """Chunk an ExtractedDocument into overlapping text segments with page/header metadata.

        Args:
            doc: ExtractedDocument object.

        Returns:
            List of ChunkData objects.
        """
        raw_text = doc.raw_text
        if not raw_text or not raw_text.strip():
            return []

        # Build page character range index: (page_num, start_char, end_char, headers)
        page_ranges: list[tuple[int, int, int, list[str]]] = []
        current_offset = 0
        for page in doc.pages:
            page_len = len(page.text)
            end_offset = current_offset + page_len
            page_ranges.append((page.page_number, current_offset, end_offset, page.headers))
            # Account for "\n\n" joiner between pages
            current_offset = end_offset + 2

        chunks: list[ChunkData] = []
        full_length = len(raw_text)
        start_idx = 0
        chunk_counter = 0

        while start_idx < full_length:
            end_idx = min(start_idx + self.chunk_size, full_length)

            # Try to break at a natural boundary (paragraph or sentence) if not at end of text
            if end_idx < full_length:
                # Look for paragraph break (\n\n) near end_idx
                search_sub = raw_text[max(start_idx, end_idx - 200):end_idx]
                para_break = search_sub.rfind("\n\n")
                if para_break != -1:
                    end_idx = max(start_idx, end_idx - 200) + para_break + 2
                else:
                    # Look for sentence break (. ) near end_idx
                    sent_break = search_sub.rfind(". ")
                    if sent_break != -1:
                        end_idx = max(start_idx, end_idx - 200) + sent_break + 2

            raw_chunk_text = raw_text[start_idx:end_idx]
            clean_chunk_text = normalize_text(raw_chunk_text)

            if clean_chunk_text:
                # Find associated page number and headers
                page_num = None
                headers_found = []
                for p_num, p_start, p_end, p_headers in page_ranges:
                    if not (end_idx <= p_start or start_idx >= p_end):
                        if page_num is None:
                            page_num = p_num
                        headers_found.extend(p_headers)

                section_header = headers_found[0] if headers_found else None
                token_estimate = max(1, len(clean_chunk_text) // 4)

                chunks.append(
                    ChunkData(
                        chunk_index=chunk_counter,
                        content=raw_chunk_text,
                        clean_content=clean_chunk_text,
                        start_char=start_idx,
                        end_char=end_idx,
                        page_number=page_num,
                        section_header=section_header,
                        token_count=token_estimate,
                    )
                )
                chunk_counter += 1

            if end_idx >= full_length:
                break

            # Move window by (chunk_size - chunk_overlap)
            step = max(1, (end_idx - start_idx) - self.chunk_overlap)
            start_idx += step

        logger.info(
            "Chunked document '%s' (%d chars) into %d chunks (size=%d, overlap=%d)",
            doc.title,
            full_length,
            len(chunks),
            self.chunk_size,
            self.chunk_overlap,
        )

        return chunks
