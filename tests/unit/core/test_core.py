"""Unit tests for core command routing behavior."""

import pytest

from mdaug.cli.commands import COMMANDS
from mdaug.schemas.io import normalize_request
from mdaug.service.runtime import run_command


@pytest.mark.parametrize("command", COMMANDS)
def test_run_command_supported(command):
    """Supported commands return list output mirrored to list request input."""
    request = normalize_request(["sample"])
    result = run_command(command, request)

    assert isinstance(result, list)
    assert result[0]["command"] == command
    assert result[0]["status"] == "not_implemented"
    assert result[0]["id"] is None
    assert "provider" in result[0]
    assert "preview" in result[0]


def test_run_command_mirrors_dictionary_shape():
    """Dictionary request input returns a dictionary-shaped response."""
    request = normalize_request({"item1": "sample"})
    result = run_command("analyze", request)

    assert isinstance(result, dict)
    assert "item1" in result
    assert result["item1"]["id"] == "item1"
    assert result["item1"]["status"] == "not_implemented"
    assert result["item1"]["provider"] == "mock"
    assert isinstance(result["item1"]["preview"], dict)


def test_run_command_invalid_command():
    """Unsupported commands return an invalid_command error payload."""
    request = normalize_request(["sample"])
    result = run_command("invalid", request)

    assert result["error"] == "invalid_command"
    assert "Unsupported command" in result["message"]
