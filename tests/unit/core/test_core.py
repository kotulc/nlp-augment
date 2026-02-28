"""Unit tests for command execution output contracts."""

import pytest

from mdaug.schemas.io import normalize_request
from mdaug.service.runtime import run_command


@pytest.mark.parametrize(
    "command,payload",
    [
        ("analyze", ["Alpha beta"]),
        ("extract", ["Alpha beta gamma"]),
        ("outline", ["Alpha beta gamma delta"]),
        ("summarize", ["Alpha beta gamma delta"]),
        ("tag", ["Alpha beta gamma delta"]),
        ("title", ["Alpha beta gamma delta"]),
    ],
)
def test_item_commands_return_list_for_list_input(command, payload):
    """Per-item commands return one output object per list input item."""
    request = normalize_request(payload)
    result = run_command(command, request)

    assert isinstance(result, list)
    assert len(result) == len(payload)
    assert isinstance(result[0], dict)


def test_item_commands_return_dict_for_dict_input():
    """Per-item commands return dictionary-shaped output for keyed input."""
    request = normalize_request({"item1": "alpha beta"})
    result = run_command("analyze", request)

    assert isinstance(result, dict)
    assert "item1" in result
    assert "positive" in result["item1"]


@pytest.mark.parametrize("command", ["compare", "rank"])
def test_group_commands_return_set_level_dict_for_list_input(command):
    """Set-level commands return dictionary scores for list input."""
    request = normalize_request(["first content", "second content", "third content"])
    result = run_command(command, request)

    assert isinstance(result, dict)
    assert len(result) == 2


def test_compare_uses_candidate_content_keys_for_list_shape():
    """Compare list input keys correspond to candidate content strings."""
    request = normalize_request(["query terms", "query terms extra", "other words"])
    result = run_command("compare", request)

    assert "query terms extra" in result
    assert "other words" in result


def test_compare_uses_candidate_ids_for_dict_shape():
    """Compare dictionary input keys correspond to candidate item ids."""
    request = normalize_request({"q": "query", "a": "query match", "b": "different"})
    result = run_command("compare", request)

    assert set(result.keys()) == {"a", "b"}


def test_run_command_invalid_command():
    """Unsupported commands return a structured invalid_command payload."""
    request = normalize_request(["sample"])
    result = run_command("invalid", request)

    assert result["error"] == "invalid_command"
    assert "Unsupported command" in result["message"]
