"""Provider-backed operation execution aligned with CLI output contracts."""

from mdaug.providers.factory import ProviderBundle
from mdaug.schemas.io import RequestGroup


ITEM_COMMANDS = {"analyze", "extract", "outline", "summarize", "tag", "title"}
GROUP_COMMANDS = {"compare", "rank"}


def _sorted_scores(scores: dict[str, float]) -> dict[str, float]:
    """Sort score mappings from highest to lowest value."""
    sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return {key: value for key, value in sorted_items}


def run_item_operation(command: str, content: str, providers: ProviderBundle) -> dict:
    """Execute a per-item command and return command-specific output."""
    if command == "analyze":
        return providers.analysis.analyze(content)
    if command == "extract":
        return providers.extraction.extract(content)
    if command in {"outline", "summarize", "tag", "title"}:
        generated = providers.generative.generate(content, operation=command)
        return _sorted_scores(generated)

    raise ValueError(f"Unsupported per-item command: {command}")


def run_group_operation(command: str, group: RequestGroup, providers: ProviderBundle) -> dict:
    """Execute a set-level command using all items in a request group."""
    items = group.iter_items()
    if len(items) < 2:
        return {}

    query_id, query_content = items[0]
    candidate_items = items[1:]
    candidate_contents = [content for _, content in candidate_items]
    candidate_scores = providers.relevance.score(query_content, candidate_contents)

    if group.shape == "list":
        mapping = candidate_scores
    else:
        mapping = {
            item_id: candidate_scores.get(content, 0.0)
            for item_id, content in candidate_items
            if item_id is not None
        }

    sorted_mapping = _sorted_scores(mapping)
    if command == "compare":
        return sorted_mapping

    # For rank, bias toward concise candidates to differ from compare.
    adjusted = {}
    for key, score in sorted_mapping.items():
        word_count = len(key.split()) if isinstance(key, str) else 1
        adjusted[key] = round(max(0.0, score * (1.0 - min(0.3, word_count * 0.02))), 3)

    return _sorted_scores(adjusted)
