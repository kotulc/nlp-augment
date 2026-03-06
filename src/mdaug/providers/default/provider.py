"""Default model-backed provider implementations for command runtime behavior."""

import re

from mdaug.providers.interfaces import (
    AnalysisProvider,
    ExtractionProvider,
    GenerativeProvider,
    RelevanceProvider,
)
from mdaug.providers.default.models import (
    get_document_model,
    get_generative_model,
    get_keyword_model,
    get_polarity_model,
    get_spam_model,
    get_sentiment_model,
    get_toxicity_model,
)
from mdaug.providers.default.relevance import (
    composite_scores,
    semantic_similarity,
)


DEFAULT_TEMPLATE = "{prompt}:\n\nText: {content}\n\n{delimiter}"
MODEL_PROMPTS = {
    "outline": [
        "In as few words as possible, outline the following text",
        "List concise bullet-like points describing the key ideas of the following text",
    ],
    "summarize": [
        "Provide a brief summary of the following text",
        "List several concise 2-8 word summaries for the following text",
    ],
    "tag": [
        "With as few words as possible, list high-level topics from the following text",
        "With as few words as possible, list related concepts from the following text",
    ],
    "title": [
        "In 5 words or less, list concise and engaging titles for the following text",
        "List short headline-style alternatives for the following text",
    ],
}


def _parsed_candidates(responses: list[str], operation: str) -> list[str]:
    """Parse generated responses into clean candidate phrases."""
    if operation in {"outline", "tag"}:
        pattern = r"[.,:;<>\[\]`|\n*-]|\*\*|--|---"
    else:
        pattern = r"[.,:;<>\[\]`|\n]"

    candidates = []
    for response in responses:
        if len(response) < 2:
            continue

        parts = re.split(pattern, response)
        for part in parts:
            phrase = part.strip()
            if len(phrase) < 2:
                continue
            if not re.search(r"[a-zA-Z]", phrase):
                continue
            candidates.append(" ".join(phrase.split()))

    return list(dict.fromkeys(candidates))


def _candidate_filters(candidates: list[str], operation: str) -> list[str]:
    """Apply operation-specific candidate length filtering."""
    filtered = []
    for candidate in candidates:
        word_count = len(candidate.split())
        if operation == "tag" and not (1 <= word_count <= 3):
            continue
        if operation == "title" and word_count > 8:
            continue
        if operation == "summarize" and word_count > 18:
            continue
        filtered.append(candidate)

    return filtered


class DefaultAnalysisProvider(AnalysisProvider):
    """Analysis provider backed by sentiment and toxicity models."""

    def analyze(self, content: str) -> dict:
        sentiment_scores = get_sentiment_model()(content)
        polarity_score = float(get_polarity_model()(content)["score"])
        spam_score = float(get_spam_model()(content)["score"])
        toxicity_score = float(get_toxicity_model()(content)["score"])

        return {
            "negative": round(float(sentiment_scores["negative"]), 4),
            "neutral": round(float(sentiment_scores["neutral"]), 4),
            "positive": round(float(sentiment_scores["positive"]), 4),
            "polarity": round(polarity_score, 4),
            "spam": round(spam_score, 4),
            "toxicity": round(toxicity_score, 4),
        }


class DefaultExtractionProvider(ExtractionProvider):
    """Extraction provider backed by entity and keyword logic."""

    def extract(self, content: str) -> dict:
        doc_model = get_document_model()
        keyword_model = get_keyword_model(top_n=10)

        entities = [entity.text.strip() for entity in doc_model(content).ents if entity.text.strip()]
        entity_candidates, entity_scores = semantic_similarity(content, entities)

        keywords = keyword_model(content)
        keyword_candidates, keyword_scores = semantic_similarity(content, keywords)

        return {
            "entities": {
                candidate: score
                for candidate, score in zip(entity_candidates[:5], entity_scores[:5])
            },
            "keywords": {
                candidate: score
                for candidate, score in zip(keyword_candidates[:10], keyword_scores[:10])
            },
        }


class DefaultGenerativeProvider(GenerativeProvider):
    """Generative provider using prompt templates and scored candidate parsing."""

    def generate(self, content: str, operation: str) -> dict:
        if operation not in MODEL_PROMPTS:
            raise ValueError(f"Unsupported generation operation: {operation}")

        generator = get_generative_model()
        prompt_kwargs = {"max_new_tokens": 96, "num_return_sequences": 3, "temperature": 0.7}
        all_candidates = []

        for prompt in MODEL_PROMPTS[operation]:
            delimiter = f"<|{operation}|>:" if operation in {"outline", "tag"} else "Output:"
            text_prompt = DEFAULT_TEMPLATE.format(prompt=prompt, content=content, delimiter=delimiter)
            responses = generator(text_prompt, **prompt_kwargs)
            all_candidates.extend(_parsed_candidates(responses, operation=operation))

        filtered_candidates = _candidate_filters(all_candidates, operation=operation)
        ranked_candidates, ranked_scores = composite_scores(content, filtered_candidates)

        result = {}
        for candidate, score in zip(ranked_candidates[:10], ranked_scores[:10]):
            result[candidate] = float(score)

        return result


class DefaultRelevanceProvider(RelevanceProvider):
    """Relevance provider backed by semantic similarity scoring."""

    def score(self, content: str, candidates: list[str]) -> dict:
        ranked_candidates, ranked_scores = semantic_similarity(content, candidates)
        return {
            candidate: float(score)
            for candidate, score in zip(ranked_candidates, ranked_scores)
        }
