"""Executable contract checks for documented examples and command outputs."""

import io
import json
from pathlib import Path

import pytest

from mdaug.cli.app import main


@pytest.mark.parametrize(
    "command,example_path,expected_top_type",
    [
        ("analyze", "examples/analyze.json", list),
        ("compare", "examples/compare.json", dict),
        ("extract", "examples/extract.json", list),
        ("outline", "examples/outline.json", list),
        ("rank", "examples/rank.json", dict),
        ("summarize", "examples/summarize.json", list),
        ("tag", "examples/tag.json", list),
        ("title", "examples/title.json", list),
    ],
)
def test_command_examples_execute(command, example_path, expected_top_type, tmp_path):
    """Each example file executes successfully for its command."""
    output_path = tmp_path / f"{command}.json"

    exit_code = main([command, "--file", example_path, "--out", str(output_path)])
    assert exit_code == 0

    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(result, expected_top_type)


def test_readme_cli_example_read_from_file(tmp_path):
    """README read-from-file example executes successfully."""
    output_path = tmp_path / "analyze.json"
    exit_code = main(["analyze", "--file", "examples/text.json", "--out", str(output_path)])

    assert exit_code == 0
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(result, list)


def test_readme_cli_example_pipe_stdin(monkeypatch, capsys):
    """README stdin piping example executes successfully."""
    text = Path("examples/summarize.json").read_text(encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO(text))

    exit_code = main(["summarize"])
    result = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert isinstance(result, list)


def test_readme_cli_example_write_to_file(tmp_path):
    """README --out example executes and writes JSON output."""
    output_path = tmp_path / "tagged.json"
    exit_code = main(["tag", "--file", "examples/text.json", "--out", str(output_path)])

    assert exit_code == 0
    assert output_path.exists()
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert isinstance(result, list)
