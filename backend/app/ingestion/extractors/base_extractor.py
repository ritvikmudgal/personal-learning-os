"""Base interface and data classes for document extractors."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedPage:
    """Represents text extracted from a single page/section of a document."""
    page_number: int  # 1-indexed
    text: str
    headers: list[str] = field(default_factory=list)


@dataclass
class ExtractedDocument:
    """Represents full text extracted from a document with metadata."""
    title: str
    file_path: str
    file_type: str
    pages: list[ExtractedPage]
    total_pages: int
    raw_text: str


class BaseExtractor(ABC):
    """Abstract base class for format-specific text extractors."""

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractedDocument:
        """Extract text and metadata from document file.

        Args:
            file_path: Absolute path to the file.

        Returns:
            ExtractedDocument containing pages and raw text.
        """
        pass
