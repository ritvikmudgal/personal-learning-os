"""File validation for material ingestion."""

from pathlib import Path

from app.config import get_settings


ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
    "text/x-markdown": ".md",
    "application/octet-stream": None,  # Will fallback to file extension check
}


class MaterialValidationError(Exception):
    """Raised when material validation fails."""
    pass


def validate_material_file(file_path: Path, filename: str, content_type: str | None = None) -> str:
    """Validate material file extension, existence, and size limit.

    Args:
        file_path: Absolute path to temporary/uploaded file.
        filename: Original file name.
        content_type: MIME type string.

    Returns:
        Normalized file extension (e.g. "pdf", "txt", "md").

    Raises:
        MaterialValidationError: If validation fails.
    """
    settings = get_settings()

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise MaterialValidationError(
            f"Unsupported file format '{ext}'. Allowed formats are: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    if not file_path.exists():
        raise MaterialValidationError(f"Uploaded file does not exist at path: {file_path}")

    file_size_bytes = file_path.stat().st_size
    if file_size_bytes == 0:
        raise MaterialValidationError("Uploaded file is empty (0 bytes).")

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        raise MaterialValidationError(
            f"File size ({file_size_bytes / (1024*1024):.1f}MB) exceeds maximum limit of {settings.max_upload_size_mb}MB."
        )

    return ext.lstrip(".")
