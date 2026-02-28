"""Provider-backed core operation shims for early refactor phases."""

from mdaug.providers.factory import ProviderBundle


def _provider_name(command: str, providers: ProviderBundle) -> str:
    """Return the configured provider name for a command."""
    if command == "analyze":
        return providers.names.analysis
    if command == "extract":
        return providers.names.extraction
    if command in {"compare", "rank"}:
        return providers.names.relevance
    return providers.names.generative


def run_item(command: str, item_id: str | None, content: str, providers: ProviderBundle) -> dict:
    """Run a single-item operation using provider interfaces."""
    preview: dict
    if command == "analyze":
        preview = providers.analysis.analyze(content)
    elif command == "extract":
        preview = providers.extraction.extract(content)
    elif command in {"compare", "rank"}:
        preview = providers.relevance.score(content, [content])
    else:
        preview = providers.generative.generate(content, operation=command)

    return {
        "command": command,
        "status": "not_implemented",
        "id": item_id,
        "provider": _provider_name(command, providers),
        "preview": preview,
    }
