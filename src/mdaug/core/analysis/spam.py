"""Spam and toxicity demo helpers backed by refactored providers."""

from mdaug.common.sample import (
    HAM_TEXT,
    NEGATIVE_TEXT,
    NEUTRAL_TEXT,
    POSITIVE_TEXT,
    SAMPLE_TEXT,
    SPAM_TEXT,
)
from mdaug.providers.factory import get_provider_bundle


def score_spam(content: str) -> dict[str, float]:
    """Compute a deterministic spam probability proxy."""
    lowered = content.lower()
    spam_terms = ("congratulations", "click", "won", "gift card", "claim")
    matches = sum(1 for term in spam_terms if term in lowered)
    score = min(1.0, round((matches + content.count("!")) / 6.0, 3))
    return {"spam": score}


def score_toxicity(content: str) -> dict[str, float]:
    """Compute toxicity score from analysis provider output."""
    metrics = get_provider_bundle().analysis.analyze(content)
    return {"toxicity": float(metrics["toxicity"])}


def demo_spam() -> None:
    """Run spam and toxicity demo output over standard sample texts."""
    content_labels = ("spam", "ham", "negative", "neutral", "positive", "document")
    content_strings = (SPAM_TEXT, HAM_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Spam Classification ===")
    for label, content in zip(content_labels, content_strings):
        spam = score_spam(content)["spam"]
        spam_label = "spam" if spam >= 0.5 else "ham"
        toxicity = score_toxicity(content)["toxicity"]
        toxicity_label = "toxic" if toxicity >= 0.5 else "neutral"

        print(f"\n{label.capitalize()} text: {content}")
        print(f"Prediction: {spam_label}")
        print("Spam score:", spam)
        print("Toxicity result:", {"toxicity": toxicity}, "Label:", toxicity_label)


if __name__ == "__main__":
    demo_spam()
