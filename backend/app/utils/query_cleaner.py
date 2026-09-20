"""Query cleaner utility for Layer 3 RAG & retrieval queries.

Ensures search queries are free of stringified 'null', 'None', 'undefined',
and conversational noise.
"""

import re
from typing import Optional

INVALID_TOKENS = {"null", "none", "undefined", "n/a", "nil"}

CONVERSATIONAL_PREFIXES = [
    r"^i\s+(?:don't|do\s+not)\s+want\s+to\s+study\s+(?:this|that)?",
    r"^i\s+want\s+to\s+study",
    r"^can\s+you\s+(?:please\s+)?explain",
    r"^please\s+explain",
    r"^explain\s+(?:to\s+me\s+)?",
    r"^tell\s+me\s+about",
    r"^help\s+me\s+understand",
    r"^teach\s+me",
    r"^what\s+is",
    r"^how\s+does",
    r"^i\s+(?:already\s+)?know",
    r"^continue\s+with",
]


def clean_concept_name(concept_name: Optional[str]) -> str:
    """Sanitize concept name, returning empty string if invalid or literal null."""
    if not concept_name:
        return ""
    cleaned = str(concept_name).strip()
    if cleaned.lower() in INVALID_TOKENS:
        return ""
    return cleaned


def strip_conversational_noise(text: str) -> str:
    """Strip common conversational prefixes and noise from query string."""
    cleaned = text.strip()
    for pattern in CONVERSATIONAL_PREFIXES:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    
    # Remove leading/trailing punctuation left over from prefix stripping
    cleaned = re.sub(r"^[\s,.:;?!-]+", "", cleaned).strip()
    return cleaned


def build_clean_search_query(target_concept_name: Optional[str], user_message: Optional[str]) -> str:
    """Build a clean, high-signal search query for semantic vector RAG retrieval.
    
    Ensures 'null', 'None', 'undefined' are NEVER present in search queries.
    """
    clean_target = clean_concept_name(target_concept_name)
    clean_msg = strip_conversational_noise(user_message or "") if user_message else ""
    
    # Check if cleaned message itself is just an invalid token
    if clean_msg.lower() in INVALID_TOKENS:
        clean_msg = ""
        
    if clean_target and clean_msg:
        # Avoid duplicate term if message is identical to concept name
        if clean_target.lower() in clean_msg.lower():
            query = clean_msg
        else:
            query = f"{clean_target} {clean_msg}"
    elif clean_target:
        query = clean_target
    elif clean_msg:
        query = clean_msg
    else:
        query = "learning materials"

    # Final sanity check against invalid tokens anywhere in query string
    tokens = query.split()
    filtered_tokens = [t for t in tokens if t.lower() not in INVALID_TOKENS]
    final_query = " ".join(filtered_tokens).strip()

    return final_query or "learning materials"
