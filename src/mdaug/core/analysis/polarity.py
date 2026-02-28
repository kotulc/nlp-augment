"""Polarity scoring demo helpers backed by refactored providers."""

from mdaug.common.sample import NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


def _split_sentences(content: str) -> list[str]:
    """Split text into sentence-like chunks without external dependencies."""
    chunks = [chunk.strip() for chunk in content.replace("!", ".").replace("?", ".").split(".")]
    return [chunk for chunk in chunks if chunk]


def score_polarity(content: str) -> dict[str, float]:
    """Compute deterministic polarity score from analysis provider outputs."""
    metrics = get_provider_bundle().analysis.analyze(content)
    return {"polarity": float(metrics["polarity"])}


def sentence_polarity(content: str) -> dict[str, list]:
    """Compute polarity score for each detected sentence."""
    sentences = _split_sentences(content)
    scores = [score_polarity(sentence)["polarity"] for sentence in sentences]
    return {"sentences": sentences, "scores": scores}


def demo_polarity() -> None:
    """Run polarity demo output over standard sample texts."""
    content_labels = ("negative", "neutral", "positive", "document")
    content_text = (NEGATIVE_TEXT, NEUTRAL_TEXT, POSITIVE_TEXT, SAMPLE_TEXT)

    print("\n== Document Polarity ===")
    for label, content in zip(content_labels, content_text):
        print(f"\nText: {label}")
        print("Content Polarity:", score_polarity(content))

    print("\n== Sentence Polarity ===")
    polarity_dict = sentence_polarity(SAMPLE_TEXT)
    for sentence, score in zip(polarity_dict["sentences"], polarity_dict["scores"]):
        clean_text = "'" + " ".join(sentence.split())[:60] + "...':"
        print(f"{clean_text:<64}", score)


if __name__ == "__main__":
    demo_polarity()
