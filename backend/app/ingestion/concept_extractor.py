"""LLM-based concept extractor for document text chunks."""

import json
import re
from dataclasses import dataclass
from typing import Optional

from app.llm.provider import LLMProvider
from app.utils.logging import get_logger

logger = get_logger("ingestion.concept_extractor")


@dataclass
class ExtractedConcept:
    """Dataclass representing a concept extracted from text by LLM."""
    name: str
    description: str
    domain: str
    difficulty_level: str = "intermediate"
    relevance_score: float = 1.0


CONCEPT_EXTRACTION_PROMPT = """You are a domain expert knowledge graph builder for an educational learning platform.

Analyze the following text chunk extracted from a learning material document.
Identify key educational concepts, topics, or fundamental principles taught in this text.

TEXT CHUNK:
\"\"\"
{text}
\"\"\"

INSTRUCTIONS:
1. Extract up to 5 core concepts/topics explained or referenced in this text.
2. For each concept, provide:
   - "name": Concise canonical concept name (e.g. "Gradient Descent", "Recursion", "Backpropagation")
   - "description": 1-2 sentence definition or explanation of the concept based on the text.
   - "domain": Academic/subject domain (e.g. "Computer Science", "Mathematics", "Machine Learning", "Physics").
   - "difficulty_level": One of "beginner", "intermediate", "advanced", "expert".
   - "relevance_score": Float between 0.1 and 1.0 indicating how prominently this concept is covered.

Respond ONLY with a valid JSON array of objects in this exact structure:
[
  {{
    "name": "Concept Name",
    "description": "Short description of the concept.",
    "domain": "Domain Name",
    "difficulty_level": "intermediate",
    "relevance_score": 0.95
  }}
]
Do not include any intro, markdown formatting outside json blocks, or conversational commentary.
"""


class ConceptExtractor:
    """Extract key concepts from text using LLM."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    async def extract_concepts_from_chunk(
        self, chunk_text: str, default_domain: str = "General"
    ) -> list[ExtractedConcept]:
        """Extract concepts from a single text chunk via LLM.

        Args:
            chunk_text: Cleaned text chunk.
            default_domain: Fallback domain string.

        Returns:
            List of ExtractedConcept objects.
        """
        if not chunk_text or len(chunk_text.strip()) < 50:
            return []

        prompt = CONCEPT_EXTRACTION_PROMPT.format(text=chunk_text[:3000])

        try:
            raw_response = await self.llm_provider.generate(
                prompt=prompt,
                system_prompt="You are a precise knowledge graph extraction engine. Output JSON only.",
                temperature=0.2,
            )

            # Strip JSON markdown code blocks if present
            cleaned_response = raw_response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()

            data = json.loads(cleaned_response)
            if not isinstance(data, list):
                logger.warning("LLM concept extraction response was not a JSON array: %s", cleaned_response[:100])
                return []

            extracted: list[ExtractedConcept] = []
            for item in data:
                if isinstance(item, dict) and "name" in item and item["name"].strip():
                    name = item["name"].strip()
                    desc = item.get("description", "").strip() or f"Concept extracted from text: {name}"
                    domain = item.get("domain", "").strip() or default_domain
                    diff = item.get("difficulty_level", "intermediate").strip().lower()
                    if diff not in {"beginner", "intermediate", "advanced", "expert"}:
                        diff = "intermediate"
                    rel = float(item.get("relevance_score", 1.0))
                    rel = max(0.1, min(1.0, rel))

                    extracted.append(
                        ExtractedConcept(
                            name=name,
                            description=desc,
                            domain=domain,
                            difficulty_level=diff,
                            relevance_score=rel,
                        )
                    )

            logger.info("Extracted %d concepts from chunk text prefix: %s...", len(extracted), chunk_text[:40])
            return extracted

        except Exception as e:
            logger.warning("LLM concept extraction failed or returned invalid JSON: %s", str(e))
            return []
