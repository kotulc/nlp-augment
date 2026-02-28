"""Runtime orchestration for command routing."""

from mdaug.cli.commands import COMMANDS
from mdaug.schemas.io import NormalizedRequest, map_results


def run_command(command: str, request: NormalizedRequest) -> dict | list:
    """Run a command stub and return a result mirrored to request shape."""
    if command not in COMMANDS:
        return {"error": "invalid_command", "message": f"Unsupported command: {command}"}

    return map_results(
        request=request,
        item_mapper=lambda item_id, _: {
            "command": command,
            "status": "not_implemented",
            "id": item_id,
        },
    )
