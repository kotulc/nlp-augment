"""Sentiment scoring demo helpers backed by refactored providers."""

from mdaug.common.sample import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


def _split_sentences(content: str) -> list[str]:
    """Split text into sentence-like chunks without external dependencies."""
    chunks = [chunk.strip() for chunk in content.replace("!", ".").replace("?", ".").split(".")]
    return [chunk for chunk in chunks if chunk]


def score_sentiment(content: str) -> dict[str, float]:
    """Return sentiment-style class scores from analysis provider outputs."""
    metrics = get_provider_bundle().analysis.analyze(content)
    return {
        "negative": float(metrics["negative"]),
        "neutral": float(metrics["neutral"]),
        "positive": float(metrics["positive"]),
    }


def sentence_sentiment(content: str) -> dict[str, list]:
    """Return sentiment scores for each sentence-like chunk in text."""
    sentences = _split_sentences(content)
    scores = [score_sentiment(sentence) for sentence in sentences]
    return {"sentences": sentences, "scores": scores}


def demo_sentiment() -> None:
    """Run sentiment demo output over standard sample texts."""
    content_labels = ("negative", "neutral", "positive", "document")
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Document Sentiment ===")
    for label, content in zip(content_labels, content_text):
        print(f"\nText: {label}")
        print("Content Sentiment:", score_sentiment(content))

    print("\n== Sentence Sentiment ===")
    sentiment_dict = sentence_sentiment(SAMPLE_TEXT)
    for sentence, score in zip(sentiment_dict["sentences"], sentiment_dict["scores"]):
        clean_text = "'" + " ".join(sentence.split())[:60] + "...':"
        print(f"{clean_text:<64}", score)


if __name__ == "__main__":
    demo_sentiment()
