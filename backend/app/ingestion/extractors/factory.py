"""Factory for getting document extractor by file type or extension."""

from pathlib import Path

from app.ingestion.extractors.base_extractor import BaseExtractor
from app.ingestion.extractors.markdown_extractor import MarkdownExtractor
from app.ingestion.extractors.pdf_extractor import PDFExtractor
from app.ingestion.extractors.text_extractor import TextExtractor


def get_extractor(file_path: Path) -> BaseExtractor:
    """Return appropriate extractor for file extension."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return PDFExtractor()
    elif ext == ".txt":
        return TextExtractor()
    elif ext == ".md":
        return MarkdownExtractor()
    else:
        raise ValueError(f"Unsupported file type for extraction: '{ext}'")
