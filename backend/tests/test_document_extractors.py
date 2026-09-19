"""Tests for format-specific text extractors (PDF, TXT, MD)."""

import pytest
from pathlib import Path

from app.ingestion.extractors.factory import get_extractor
from app.ingestion.extractors.markdown_extractor import MarkdownExtractor
from app.ingestion.extractors.pdf_extractor import PDFExtractor
from app.ingestion.extractors.text_extractor import TextExtractor


def test_text_extractor(tmp_path: Path):
    """Test plain text file extraction."""
    txt_file = tmp_path / "sample.txt"
    txt_file.write_text("Hello world.\nThis is a sample learning document.", encoding="utf-8")

    extractor = get_extractor(txt_file)
    assert isinstance(extractor, TextExtractor)

    doc = extractor.extract(txt_file)
    assert doc.title == "sample"
    assert doc.file_type == "txt"
    assert doc.total_pages == 1
    assert "Hello world" in doc.raw_text


def test_markdown_extractor(tmp_path: Path):
    """Test Markdown file extraction with header parsing."""
    md_file = tmp_path / "notes.md"
    md_content = """# Linear Algebra Notes

## Vector Spaces
A vector space is a set of vectors...

### Subspaces
Subspaces must contain zero vector.
"""
    md_file.write_text(md_content, encoding="utf-8")

    extractor = get_extractor(md_file)
    assert isinstance(extractor, MarkdownExtractor)

    doc = extractor.extract(md_file)
    assert doc.title == "Linear Algebra Notes"
    assert doc.file_type == "md"
    assert "Vector Spaces" in doc.pages[0].headers
    assert "Subspaces" in doc.pages[0].headers


def test_pdf_extractor(tmp_path: Path):
    """Test PDF file extraction using PyMuPDF."""
    import pymupdf as fitz

    pdf_path = tmp_path / "test_doc.pdf"
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((50, 50), "Page 1: Introduction to Machine Learning.")
    page2 = doc.new_page()
    page2.insert_text((50, 50), "Page 2: Neural Networks and Deep Learning.")
    doc.save(str(pdf_path))
    doc.close()

    extractor = get_extractor(pdf_path)
    assert isinstance(extractor, PDFExtractor)

    extracted = extractor.extract(pdf_path)
    assert extracted.file_type == "pdf"
    assert extracted.total_pages == 2
    assert "Introduction to Machine Learning" in extracted.pages[0].text
    assert "Neural Networks" in extracted.pages[1].text
