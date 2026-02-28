"""Protocol interfaces for provider implementations."""

from typing import Protocol


class AnalysisProvider(Protocol):
    """Provider contract for analysis-oriented metrics."""

    def analyze(self, content: str) -> dict:
        """Return metric scores for the supplied content."""


class ExtractionProvider(Protocol):
    """Provider contract for extraction operations."""

    def extract(self, content: str) -> dict:
        """Return entities and keywords for the supplied content."""


class GenerativeProvider(Protocol):
    """Provider contract for generation operations."""

    def generate(self, content: str, operation: str) -> dict:
        """Return generated candidates for a generation operation."""


class RelevanceProvider(Protocol):
    """Provider contract for relevance operations."""

    def score(self, content: str, candidates: list[str]) -> dict:
        """Return relevance scores for candidate content."""
