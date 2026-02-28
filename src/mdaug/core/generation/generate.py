"""Generation demo helpers backed by refactored providers."""

from mdaug.common.sample import SAMPLE_TEXT
from mdaug.providers.factory import get_provider_bundle


def generate_response(content: str, prompt: str, delimiter: str = "Output:", **kwargs) -> list[str]:
    """Generate deterministic response candidates from generative provider."""
    _ = kwargs
    operation = kwargs.get("format", "summarize")
    generated = get_provider_bundle().generative.generate(content, operation=operation)
    return [f"{prompt} {delimiter} {candidate}" for candidate in generated.keys()]


def generate_summary(
    content: str,
    prompt: str,
    format: str | None = None,
    tone: str | None = None,
    **kwargs,
) -> list[str]:
    """Generate candidate summary strings and return parsed sentence-like items."""
    prompt_text = f"{prompt} in a {tone} tone" if tone else prompt
    operation = format if format else "summarize"
    generated = get_provider_bundle().generative.generate(content, operation=operation)
    _ = kwargs
    return [f"{prompt_text}: {candidate}" for candidate in generated.keys()]


def demo_generator() -> None:
    """Run summary generation demo output over representative prompts."""
    sample_kwargs = [
        dict(content=SAMPLE_TEXT, prompt="In 5 words or less, generate several concise and engaging titles", format="title"),
        dict(content=SAMPLE_TEXT, prompt="In as few words as possible, list several tangentially related concepts", format="tag"),
        dict(content=SAMPLE_TEXT, prompt="In as few words as possible, outline the following text", format="outline"),
        dict(content=SAMPLE_TEXT, prompt="Provide a list of 2-5 word summaries of the following text", format="summarize"),
        dict(content=SAMPLE_TEXT, prompt="Briefly summarize the following text", format="summarize", tone="academic"),
    ]

    print("\n== Basic Summary ===")
    result = generate_summary(SAMPLE_TEXT, "Provide a short summary of the following text")
    print(result)

    print("\n=== With Custom Prompt ===")
    for kwargs in sample_kwargs:
        result = generate_summary(**kwargs)
        print(kwargs.get("prompt"), result)


if __name__ == "__main__":
    demo_generator()
