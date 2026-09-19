"""Plain text document extractor."""

from pathlib import Path

from app.ingestion.extractors.base_extractor import (
    BaseExtractor,
    ExtractedDocument,
    ExtractedPage,
)
from app.utils.logging import get_logger

logger = get_logger("ingestion.text_extractor")


class TextExtractor(BaseExtractor):
    """Extractor for plain text (.txt) files."""

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text from TXT file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Text file not found: {file_path}")

        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raw_text = file_path.read_text(encoding="latin-1", errors="replace")

        # TXT files have 1 page by default
        pages = [
            ExtractedPage(
                page_number=1,
                text=raw_text,
                headers=[],
            )
        ]

        logger.info("Extracted TXT '%s': %d chars", file_path.name, len(raw_text))

        return ExtractedDocument(
            title=file_path.stem,
            file_path=str(file_path),
            file_type="txt",
            pages=pages,
            total_pages=1,
            raw_text=raw_text,
        )
