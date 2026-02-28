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
        token_count = len(words)
        if token_count == 0:
            return {
                "negative": 0.0,
                "neutral": 1.0,
                "positive": 0.0,
                "polarity": 0.0,
                "toxicity": 0.0,
            }

        uppercase_count = sum(1 for character in content if character.isupper())
        exclamation_count = content.count("!")
        positive = min(1.0, round((uppercase_count + 1) / (token_count + 2), 3))
        toxicity = min(1.0, round(exclamation_count / (token_count + 1), 3))
        negative = min(1.0, round(toxicity * 0.6, 3))
        neutral = max(0.0, round(1.0 - positive - negative, 3))
        polarity = round(positive - negative, 3)

        return {
            "negative": negative,
            "neutral": neutral,
            "positive": positive,
            "polarity": polarity,
            "toxicity": toxicity,
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

        candidates = []
        candidates.append(" ".join(words[: min(3, len(words))]))
        if len(words) > 3:
            candidates.append(" ".join(words[1 : min(4, len(words))]))
        if len(words) > 4:
            candidates.append(" ".join(words[2 : min(5, len(words))]))

        unique_candidates = list(dict.fromkeys(candidate for candidate in candidates if candidate))
        return {
            candidate: round(max(0.1, 0.95 - (index * 0.08)), 3)
            for index, candidate in enumerate(unique_candidates)
        }


class MockRelevanceProvider(RelevanceProvider):
    """Mock relevance provider returning deterministic descending scores."""

    def score(self, content: str, candidates: list[str]) -> dict:
        if not candidates:
            return {}

        query_tokens = {token.lower().strip(".,!?;:") for token in content.split() if token.strip(".,!?;:")}
        return {
            candidate: round(
                max(
                    0.05,
                    (len(query_tokens & {token.lower().strip(".,!?;:") for token in candidate.split() if token})
                    + 1)
                    / (len(query_tokens) + 1),
                ),
                3,
            )
            for candidate in candidates
        }
