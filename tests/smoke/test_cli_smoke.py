"""Smoke tests for phase-1 CLI command stubs."""

import io
import json

from mdaug.cli.app import main


def test_cli_without_command_prints_help(capsys):
    """Calling CLI with no command returns success and prints usage text."""
    exit_code = main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "usage: mdaug" in output


def test_cli_command_reads_stdin_json(monkeypatch, capsys):
    """Command reads JSON from stdin and emits stub result JSON."""
    monkeypatch.setattr("sys.stdin", io.StringIO('["sample content"]'))

    exit_code = main(["analyze"])
    output = capsys.readouterr().out
    result = json.loads(output)

    assert exit_code == 0
    assert isinstance(result, list)
    assert result[0]["command"] == "analyze"
    assert result[0]["status"] == "not_implemented"
    assert result[0]["id"] is None


def test_cli_command_reads_file_and_writes_out_file(tmp_path):
    """Command reads from --file and writes JSON output to --out."""
    input_path = tmp_path / "input.json"
    output_path = tmp_path / "output.json"
    input_path.write_text('{"item1": "text"}', encoding="utf-8")

    exit_code = main(["tag", "--file", str(input_path), "--out", str(output_path)])
    result = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert isinstance(result, dict)
    assert result["item1"]["command"] == "tag"
    assert result["item1"]["status"] == "not_implemented"
    assert result["item1"]["id"] == "item1"


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
