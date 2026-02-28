"""Style-analysis demo helpers backed by deterministic heuristics."""

from mdaug.common.sample import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT


DICTION_LABELS = ("formal", "concrete", "informal", "colloquial", "literary", "poetic", "abstract")
GENRE_LABELS = ("romance", "drama", "suspense", "historical", "non-fiction", "adventure", "sci-fi", "fantasy")
MODE_LABELS = ("expository", "descriptive", "persuasive", "narrative", "creative", "experimental")
TONE_LABELS = ("dogmatic", "subjective", "neutral", "objective", "impartial")


def _label_scores(content: str, labels: tuple[str, ...]) -> dict[str, float]:
    """Generate deterministic normalized scores for a label set."""
    token_count = max(1, len(content.split()))
    scores = {}
    for index, label in enumerate(labels):
        seed = (sum(ord(char) for char in label) + token_count + index) % 97
        scores[label] = round((seed + 1) / 100.0, 4)

    total = sum(scores.values()) or 1.0
    return {label: round(score / total, 4) for label, score in scores.items()}


def classify_content(content: str, labels: tuple[str, ...], multi_label: bool = False) -> dict[str, float]:
    """Return deterministic classification scores for supplied labels."""
    _ = multi_label
    return _label_scores(content, labels)


def score_diction(content: str) -> dict[str, float]:
    """Return deterministic diction label scores."""
    return classify_content(content, DICTION_LABELS)


def score_genre(content: str) -> dict[str, float]:
    """Return deterministic genre label scores."""
    return classify_content(content, GENRE_LABELS)


def score_mode(content: str) -> dict[str, float]:
    """Return deterministic mode label scores."""
    return classify_content(content, MODE_LABELS)


def score_tone(content: str) -> dict[str, float]:
    """Return deterministic tone label scores."""
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
