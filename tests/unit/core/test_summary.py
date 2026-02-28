"""Unit tests for CLI parser contract."""

import pytest

from mdaug.cli.app import build_parser
from mdaug.cli.commands import COMMANDS


@pytest.mark.parametrize("command", COMMANDS)
def test_build_parser_supports_all_commands(command):
    """Parser accepts every documented command and optional I/O flags."""
    parser = build_parser()
    args = parser.parse_args([command, "--file", "in.json", "--out", "out.json"])

    assert args.command == command
    assert args.file_path == "in.json"
    assert args.out_path == "out.json"


def test_build_parser_requires_known_command():
    """Parser raises SystemExit for unknown command names."""
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["unknown"])
