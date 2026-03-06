"""Style-analysis demo helpers backed by configured provider relevance scoring."""

from mdaug.common.sample import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


DICTION_LABELS = ("formal", "concrete", "informal", "colloquial", "literary", "poetic", "abstract")
GENRE_LABELS = ("romance", "drama", "suspense", "historical", "non-fiction", "adventure", "sci-fi", "fantasy")
MODE_LABELS = ("expository", "descriptive", "persuasive", "narrative", "creative", "experimental")
TONE_LABELS = ("dogmatic", "subjective", "neutral", "objective", "impartial")


def _label_scores(content: str, labels: tuple[str, ...]) -> dict[str, float]:
    """Score labels by semantic similarity through the configured relevance provider."""
    candidates = [f"{label} writing style" for label in labels]
    provider_scores = get_provider_bundle().relevance.score(content, candidates)
    scores = {label: float(provider_scores.get(candidate, 0.0)) for label, candidate in zip(labels, candidates)}
    total = sum(scores.values())
    if total <= 0.0:
        uniform = round(1.0 / max(1, len(labels)), 4)
        return {label: uniform for label in labels}

    return {label: round(score / total, 4) for label, score in scores.items()}


def classify_content(content: str, labels: tuple[str, ...], multi_label: bool = False) -> dict[str, float]:
    """Return provider-scored label distribution for supplied style labels."""
    _ = multi_label
    return _label_scores(content, labels)


def score_diction(content: str) -> dict[str, float]:
    """Return diction label scores from provider-backed similarity scoring."""
    return classify_content(content, DICTION_LABELS)


def score_genre(content: str) -> dict[str, float]:
    """Return genre label scores from provider-backed similarity scoring."""
    return classify_content(content, GENRE_LABELS)


def score_mode(content: str) -> dict[str, float]:
    """Return mode label scores from provider-backed similarity scoring."""
    return classify_content(content, MODE_LABELS)


def score_tone(content: str) -> dict[str, float]:
    """Return tone label scores from provider-backed similarity scoring."""
    return classify_content(content, TONE_LABELS)


def demo_style() -> None:
    """Run style scoring demo output over standard sample texts."""
    content_labels = ("negative", "neutral", "positive", "document")
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Document Analysis ===")
    for content_label, content in zip(content_labels, content_text):
        print(f"\nText: {content_label}")
        print("Diction scores:", score_diction(content))
        print("Genre scores:", score_genre(content))
        print("Mode scores:", score_mode(content))
        print("Tone scores:", score_tone(content))


if __name__ == "__main__":
    demo_style()
