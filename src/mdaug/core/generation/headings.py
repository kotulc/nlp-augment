"""Heading and outline demo helpers backed by refactored providers."""

from mdaug.common.sample import SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


HEADING_OPERATIONS = {
    "title": "title",
    "subtitle": "title",
    "description": "summarize",
}


def get_headings(content: str, heading: str, top_n: int) -> tuple[list[str], list[float]]:
    """Generate heading candidates and scores for the selected heading type."""
    if heading not in HEADING_OPERATIONS:
        raise ValueError(f"Unsupported heading type '{heading}'.")

    operation = HEADING_OPERATIONS[heading]
    generated = get_provider_bundle().generative.generate(content, operation=operation)
    items = list(generated.items())[:top_n]
    candidates = [candidate for candidate, _ in items]
    scores = [float(score) for _, score in items]
    return candidates, scores


def get_title(content: str, top_n: int = 3) -> tuple[list[str], list[float]]:
    """Generate title candidates and scores."""
    return get_headings(content, heading="title", top_n=top_n)


def get_subtitle(content: str, top_n: int = 3) -> tuple[list[str], list[float]]:
    """Generate subtitle candidates and scores."""
    return get_headings(content, heading="subtitle", top_n=top_n)


def get_description(content: str, top_n: int = 3) -> tuple[list[str], list[float]]:
    """Generate short description candidates and scores."""
    return get_headings(content, heading="description", top_n=top_n)


def get_outline(content: str, n_sections: int = 3) -> tuple[list[str], list[float]]:
    """Generate outline candidates from section-like chunks."""
    sections = [section.strip() for section in content.split(".") if section.strip()]
    if not sections:
        raise ValueError("Supplied content string must contain one or more sentences.")

    selected_sections = sections[:n_sections]
    summaries = []
    scores = []
    for section in selected_sections:
        generated = get_provider_bundle().generative.generate(section, operation="outline")
        if generated:
            top_key = next(iter(generated.keys()))
            top_score = generated[top_key]
            summaries.append(top_key)
            scores.append(float(top_score))

    return summaries, scores


def demo_headings() -> None:
    """Run heading and outline demo outputs."""
    n_sections = 3
    top_n = 5

    print("\n=== Generate Headings ===")
    for heading in HEADING_OPERATIONS.keys():
        result = get_headings(SAMPLE_TEXT, heading=heading, top_n=top_n)
        print(f"\nGenerated {heading}s:", result)

    print("\n=== Generate Outline ===")
    summaries, scores = get_outline(SAMPLE_TEXT, n_sections=n_sections)
    for index, (summary, score) in enumerate(zip(summaries, scores), start=1):
        print(f"\nOutline candidate {index}:")
        print("\t-", summary, score)


if __name__ == "__main__":
    demo_headings()
