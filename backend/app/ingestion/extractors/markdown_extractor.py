"""Markdown document extractor with header parsing."""

import re
from pathlib import Path

from app.ingestion.extractors.base_extractor import (
    BaseExtractor,
    ExtractedDocument,
    ExtractedPage,
)
from app.utils.logging import get_logger

logger = get_logger("ingestion.markdown_extractor")

HEADER_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


class MarkdownExtractor(BaseExtractor):
    """Extractor for Markdown (.md) files."""

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text and section headers from Markdown file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = file_path.read_text(encoding="latin-1", errors="replace")

        headers = [match.group(2).strip() for match in HEADER_PATTERN.finditer(raw_text)]

        # Extract title from first H1 header or file stem
        title = file_path.stem
        h1_match = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()

        pages = [
            ExtractedPage(
                page_number=1,
                text=raw_text,
                headers=headers,
            )
        ]

        logger.info("Extracted Markdown '%s': title='%s', headers=%d", file_path.name, title, len(headers))

        return ExtractedDocument(
            title=title,
            file_path=str(file_path),
            file_type="md",
            pages=pages,
            total_pages=1,
            raw_text=raw_text,
        )
