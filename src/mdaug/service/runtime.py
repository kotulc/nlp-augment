"""Runtime orchestration for command routing."""

from mdaug.cli.commands import COMMANDS
from mdaug.schemas.io import get_payload_type


def run_command(command: str, payload: object) -> dict:
    """Run a command stub and return a normalized placeholder response."""
    if command not in COMMANDS:
        return {"error": "invalid_command", "message": f"Unsupported command: {command}"}

    return {
        "command": command,
        "status": "not_implemented",
        "payload_type": get_payload_type(payload),
    }
