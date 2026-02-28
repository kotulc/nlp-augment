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
    assert result[0]["provider"] == "mock"
    assert "length" in result[0]["preview"]


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
    assert result["item1"]["provider"] == "mock"


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
