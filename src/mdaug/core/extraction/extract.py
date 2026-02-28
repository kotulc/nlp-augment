"""Extraction demo helpers backed by refactored providers."""

from mdaug.common.sample import SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


def extract_entities(content: str, top_n: int = 5) -> tuple[list[str], list[float]]:
    """Extract top entity keys and synthetic scores."""
    entities = get_provider_bundle().extraction.extract(content).get("entities", {})
    keys = list(entities.keys())[:top_n]
    scores = [float(entities[key]) for key in keys]
    return keys, scores


def extract_keywords(content: str, top_n: int = 10) -> tuple[list[str], list[float]]:
    """Extract top keyword keys and their scores."""
    keywords = get_provider_bundle().extraction.extract(content).get("keywords", {})
    keys = list(keywords.keys())[:top_n]
    scores = [float(keywords[key]) for key in keys]
    return keys, scores


def extract_related(
    content: str,
    min_length: int = 1,
    max_length: int = 3,
    top_n: int = 10,
) -> tuple[list[str], list[float]]:
    """Generate related tags via generative provider and apply length filters."""
    generated = get_provider_bundle().generative.generate(content, operation="tag")
    items = [(tag, score) for tag, score in generated.items() if min_length <= len(tag.split()) <= max_length]
    items = items[:top_n]
    tags = [tag for tag, _ in items]
    scores = [float(score) for _, score in items]
    return tags, scores


def demo_tagger() -> None:
    """Run extraction demo output for entities, keywords, and related tags."""
    print("\n=== Basic Tagging ===")
    print("\nExtracted entities:", extract_entities(SAMPLE_TEXT, top_n=5))
    print("\nExtracted keywords:", extract_keywords(SAMPLE_TEXT, top_n=8))
    print("\nExtracted related tags (min ngram=1):", extract_related(SAMPLE_TEXT, min_length=1, max_length=3, top_n=5))
    print("\nExtracted related tags (min ngram=2):", extract_related(SAMPLE_TEXT, min_length=2, max_length=5, top_n=5))


if __name__ == "__main__":
    demo_tagger()
