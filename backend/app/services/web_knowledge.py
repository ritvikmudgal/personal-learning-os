"""Web knowledge retriever — clean boundary interface for future web retrieval integration.

Defines the contract for external/web search knowledge retrieval without locking
the teaching engine to local-only or web-only sources.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WebSearchResult:
    """A web search result item."""
    title: str
    url: str
    snippet: str
    source_domain: str
    relevance_score: float = 1.0


@dataclass
class WebKnowledgeResponse:
    """Aggregated web knowledge search response."""
    query: str
    results: list[WebSearchResult] = field(default_factory=list)
    is_available: bool = False
    message: str = "Web retrieval tool boundary initialized."


class BaseWebKnowledgeRetriever(ABC):
    """Abstract interface boundary for web knowledge retrieval."""

    @abstractmethod
    async def search_web_knowledge(
        self,
        query: str,
        concept_name: Optional[str] = None,
        limit: int = 3,
    ) -> WebKnowledgeResponse:
        """Retrieve web knowledge for a topic or search query."""
        ...


class StubWebKnowledgeRetriever(BaseWebKnowledgeRetriever):
    """Stub implementation of WebKnowledgeRetriever for Layer 4.

    Will be extended in future layers without altering the learning engine architecture.
    """

    async def search_web_knowledge(
        self,
        query: str,
        concept_name: Optional[str] = None,
        limit: int = 3,
    ) -> WebKnowledgeResponse:
        """Return stub response indicating boundary readiness."""
        return WebKnowledgeResponse(
            query=query,
            results=[],
            is_available=False,
            message="Web retrieval boundary ready (local material & learner memory active).",
        )
