"""Tests for text chunker, sliding window, overlap, and provenance metadata."""

import pytest

from app.ingestion.chunker import TextChunker
from app.ingestion.extractors.base_extractor import ExtractedDocument, ExtractedPage
from app.ingestion.normalizer import normalize_text


def test_text_normalizer():
    """Test text cleaning and unicode normalization."""
    raw = "Hello   world!\r\n\r\n\r\nComput-\nations in  python.\u200b"
    clean = normalize_text(raw)
    assert "Hello world!" in clean
    assert "Computations in python." in clean
    assert "\n\n\n" not in clean


def test_chunker_sliding_window():
    """Test chunker splits text into overlapping segments with metadata."""
    sample_text = ("Word " * 600)  # ~3000 chars

    doc = ExtractedDocument(
        title="Sample",
        file_path="/tmp/sample.txt",
        file_type="txt",
        pages=[ExtractedPage(page_number=1, text=sample_text, headers=["Overview"])],
        total_pages=1,
        raw_text=sample_text,
    )

    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) >= 2
    assert chunks[0].chunk_index == 0
    assert chunks[0].page_number == 1
    assert chunks[0].section_header == "Overview"
    assert chunks[0].start_char == 0
    assert chunks[0].end_char <= 1000
    assert chunks[1].start_char < chunks[0].end_char  # Verify overlap
