"""Unit tests for core command routing behavior."""

import pytest

from mdaug.cli.commands import COMMANDS
from mdaug.service.runtime import run_command


@pytest.mark.parametrize("command", COMMANDS)
def test_run_command_supported(command):
    """Supported commands return a not_implemented status payload."""
    result = run_command(command, ["sample"])

    assert result["command"] == command
    assert result["status"] == "not_implemented"
    assert result["payload_type"] == "list"


def test_run_command_invalid_command():
    """Unsupported commands return an invalid_command error payload."""
    result = run_command("invalid", ["sample"])

    assert result["error"] == "invalid_command"
    assert "Unsupported command" in result["message"]
