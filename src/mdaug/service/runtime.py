"""Runtime orchestration for command routing."""

from mdaug.cli.commands import COMMANDS
from mdaug.core.operations import run_item
from mdaug.providers.factory import get_provider_bundle
from mdaug.schemas.io import NormalizedRequest, map_results


def run_command(command: str, request: NormalizedRequest) -> dict | list:
    """Run a command stub and return a result mirrored to request shape."""
    if command not in COMMANDS:
        return {"error": "invalid_command", "message": f"Unsupported command: {command}"}

    providers = get_provider_bundle()
    return map_results(
        request=request,
        item_mapper=lambda item_id, content: run_item(
            command=command,
            item_id=item_id,
            content=content,
            providers=providers,
        ),
    )
