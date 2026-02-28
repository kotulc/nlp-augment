"""Unit tests for CLI command metadata."""

from mdaug.cli.commands import COMMANDS


def test_commands_are_unique():
    """Command declarations are unique to prevent parser conflicts."""
    assert len(COMMANDS) == len(set(COMMANDS))


def test_commands_match_spec_set():
    """Command list matches the documented operation set."""
    expected = {
        "analyze",
        "compare",
        "extract",
        "outline",
        "rank",
        "summarize",
        "tag",
        "title",
    }
    assert set(COMMANDS) == expected
