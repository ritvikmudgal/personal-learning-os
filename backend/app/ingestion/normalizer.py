"""Text normalization utilities for document ingestion."""

import re
import unicodedata


def normalize_text(text: str) -> str:
    """Clean and normalize raw extracted text.

    Args:
        text: Raw text string extracted from document.

    Returns:
        Normalized clean text string.
    """
    if not text:
        return ""

    # 1. Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)

    # 2. Fix hyphenation split across line breaks (e.g., "comput-\nation" -> "computation")
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    # 3. Replace non-standard whitespace characters (carriage returns, form feeds, tabs, etc.)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[\t\f\v\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]", " ", text)

    # 4. Collapse multiple inline spaces while preserving newlines
    lines = [re.sub(r" {2,}", " ", line.strip()) for line in text.splitlines()]

    # 5. Collapse 3+ consecutive newlines into double newlines (paragraph boundaries)
    cleaned_text = "\n".join(lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)

    return cleaned_text.strip()
