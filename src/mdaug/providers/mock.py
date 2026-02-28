"""Deterministic mock providers used for testing and early refactor phases."""

from mdaug.providers.interfaces import (
    AnalysisProvider,
    ExtractionProvider,
    GenerativeProvider,
    RelevanceProvider,
)


class MockAnalysisProvider(AnalysisProvider):
    """Mock analysis provider with deterministic metric-like output."""

    def analyze(self, content: str) -> dict:
        words = [word for word in content.split() if word]
        return {
            "length": float(len(content)),
            "tokens": float(len(words)),
        }


class MockExtractionProvider(ExtractionProvider):
    """Mock extraction provider with deterministic keywords/entities output."""

    def extract(self, content: str) -> dict:
        words = [word.strip(".,!?;:").lower() for word in content.split() if word.strip(".,!?;:")]
        unique_words = list(dict.fromkeys(words))
        keywords = {word: round(1.0 - (index * 0.1), 3) for index, word in enumerate(unique_words[:5])}
        return {"entities": {}, "keywords": keywords}


class MockGenerativeProvider(GenerativeProvider):
    """Mock generation provider returning operation-scoped candidate scores."""

    def generate(self, content: str, operation: str) -> dict:
        words = [word.strip(".,!?;:") for word in content.split() if word.strip(".,!?;:")]
        if not words:
            return {}

        title = " ".join(words[: min(3, len(words))])
        return {f"{operation}:{title}": 0.9}


class MockRelevanceProvider(RelevanceProvider):
    """Mock relevance provider returning deterministic descending scores."""

    def score(self, content: str, candidates: list[str]) -> dict:
        if not candidates:
            return {}

        return {
            candidate: round(1.0 - (index * 0.1), 3)
            for index, candidate in enumerate(candidates)
        }
