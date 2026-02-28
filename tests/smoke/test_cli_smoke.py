"""Smoke tests for CLI I/O contracts and command output shapes."""

import io
import json

import pytest

from mdaug.cli.app import main


def test_cli_without_command_prints_help(capsys):
    """Calling CLI with no command returns success and prints usage text."""
    exit_code = main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "usage: mdaug" in output


@pytest.mark.parametrize(
    "command,stdin_payload,assertion_key",
    [
        ("analyze", '["Sample input"]', "positive"),
        ("extract", '["Sample input"]', "keywords"),
        ("outline", '["Sample input for outline"]', None),
        ("summarize", '["Sample input for summarize"]', None),
        ("tag", '["Sample input for tag"]', None),
        ("title", '["Sample input for title"]', None),
    ],
)
def test_cli_item_commands_read_stdin_json(monkeypatch, capsys, command, stdin_payload, assertion_key):
    """Item commands read stdin JSON and return list-shaped results."""
    monkeypatch.setattr("sys.stdin", io.StringIO(stdin_payload))

    exit_code = main([command])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    if assertion_key is not None:
        assert assertion_key in result[0]


@pytest.mark.parametrize("command", ["compare", "rank"])
def test_cli_group_commands_return_set_level_dict(monkeypatch, capsys, command):
    """Compare and rank return set-level dictionary output for list input."""
    payload = '["query content", "candidate one", "candidate two"]'
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))

    exit_code = main([command])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert isinstance(result, dict)
    assert len(result) == 2


def test_cli_command_reads_file_and_writes_out_file(tmp_path):
    """Command reads from --file and writes JSON output to --out."""
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text('{"item1": "text"}', encoding="utf-8")

    exit_code = main(["analyze", "--file", str(input_path), "--out", str(output_path)])
    result = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert isinstance(result, dict)
    assert "item1" in result
    assert "positive" in result["item1"]


def test_cli_invalid_json_returns_error(tmp_path):
    """Invalid JSON input returns a non-zero exit code and error payload."""
    input_path = tmp_path / "broken.json"
    output_path = tmp_path / "output.json"
    input_path.write_text('{"missing": "quote}', encoding="utf-8")

    exit_code = main(["summarize", "--file", str(input_path), "--out", str(output_path)])
    result = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 1
    assert result["error"] == "invalid_json"


def test_cli_missing_input_returns_error(monkeypatch, capsys):
    """Empty stdin input returns a missing_input validation error."""
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    exit_code = main(["compare"])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert result["error"] == "missing_input"


def test_cli_rejects_file_and_stdin_together(monkeypatch, tmp_path, capsys):
    """Supplying both --file and stdin input returns an input-source error."""
    input_path = tmp_path / "input.json"
    input_path.write_text('["file content"]', encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO('["stdin content"]'))

    exit_code = main(["analyze", "--file", str(input_path)])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert result["error"] == "invalid_input_source"


def test_cli_invalid_output_path_returns_error(monkeypatch, tmp_path, capsys):
    """Invalid --out destination returns invalid_output and non-zero exit code."""
    monkeypatch.setattr("sys.stdin", io.StringIO('["sample"]'))

    exit_code = main(["analyze", "--out", str(tmp_path)])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert result["error"] == "invalid_output"


def test_cli_missing_required_content_returns_error(monkeypatch, capsys):
    """Dictionary values must be strings; null values fail validation."""
    monkeypatch.setattr("sys.stdin", io.StringIO('{"item1": null}'))

    exit_code = main(["extract"])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert result["error"] == "invalid_input"
