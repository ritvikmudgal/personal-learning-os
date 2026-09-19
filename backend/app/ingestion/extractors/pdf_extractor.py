"""PDF extractor using PyMuPDF (fitz)."""

from pathlib import Path
import pymupdf as fitz

from app.ingestion.extractors.base_extractor import (
    BaseExtractor,
    ExtractedDocument,
    ExtractedPage,
)
from app.utils.logging import get_logger

logger = get_logger("ingestion.pdf_extractor")


class PDFExtractor(BaseExtractor):
    """Extract text page by page from PDF files using PyMuPDF."""

    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text from PDF file."""
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        doc = fitz.open(str(file_path))
        pages: list[ExtractedPage] = []
        full_text_chunks: list[str] = []

        try:
            total_pages = len(doc)
            doc_title = doc.metadata.get("title") or file_path.stem

            for page_idx in range(total_pages):
                page = doc.load_page(page_idx)
                page_text = page.get_text("text") or ""
                
                # Simple section header heuristic (first non-empty line if short)
                headers = []
                lines = [l.strip() for l in page_text.splitlines() if l.strip()]
                if lines and len(lines[0]) < 80 and not lines[0].endswith("."):
                    headers.append(lines[0])

                pages.append(
                    ExtractedPage(
                        page_number=page_idx + 1,
                        text=page_text,
                        headers=headers,
                    )
                )
                full_text_chunks.append(page_text)

            raw_text = "\n\n".join(full_text_chunks)
            logger.info("Extracted PDF '%s': %d pages, %d chars", file_path.name, total_pages, len(raw_text))

            return ExtractedDocument(
                title=doc_title,
                file_path=str(file_path),
                file_type="pdf",
                pages=pages,
                total_pages=total_pages,
                raw_text=raw_text,
            )
        finally:
            doc.close()
