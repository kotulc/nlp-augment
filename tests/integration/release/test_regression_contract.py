"""Release regression checks for command contracts and batch sanity."""

import io
import json
import time

import pytest

from mdaug.cli.app import main


ITEM_COMMANDS = ("analyze", "extract", "outline", "summarize", "tag", "title")
GROUP_COMMANDS = ("compare", "rank")


@pytest.mark.parametrize("command", ITEM_COMMANDS)
def test_item_commands_regression_list_and_dict_inputs(monkeypatch, capsys, command):
    """Per-item commands preserve list/dict output shape contracts."""
    monkeypatch.setattr("sys.stdin", io.StringIO('["alpha", "beta"]'))
    list_exit = main([command])
    list_result = json.loads(capsys.readouterr().out)
    assert list_exit == 0
    assert isinstance(list_result, list)
    assert len(list_result) == 2

    monkeypatch.setattr("sys.stdin", io.StringIO('{"a": "alpha", "b": "beta"}'))
    dict_exit = main([command])
    dict_result = json.loads(capsys.readouterr().out)
    assert dict_exit == 0
    assert isinstance(dict_result, dict)
    assert set(dict_result.keys()) == {"a", "b"}


@pytest.mark.parametrize("command", GROUP_COMMANDS)
def test_group_commands_regression_list_and_dict_inputs(monkeypatch, capsys, command):
    """Set-level commands return score dictionaries for list/dict requests."""
    monkeypatch.setattr("sys.stdin", io.StringIO('["query", "candidate a", "candidate b"]'))
    list_exit = main([command])
    list_result = json.loads(capsys.readouterr().out)
    assert list_exit == 0
    assert isinstance(list_result, dict)
    assert len(list_result) == 2

    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO('{"q": "query", "a": "candidate a", "b": "candidate b"}'),
    )
    dict_exit = main([command])
    dict_result = json.loads(capsys.readouterr().out)
    assert dict_exit == 0
    assert isinstance(dict_result, dict)
    assert set(dict_result.keys()) == {"a", "b"}


@pytest.mark.parametrize("command", ITEM_COMMANDS)
def test_item_commands_regression_grouped_inputs(monkeypatch, capsys, command):
    """Per-item commands preserve grouped list/dict top-level output shape."""
    monkeypatch.setattr("sys.stdin", io.StringIO('[["alpha"], ["beta"]]'))
    grouped_list_exit = main([command])
    grouped_list_result = json.loads(capsys.readouterr().out)
    assert grouped_list_exit == 0
    assert isinstance(grouped_list_result, list)
    assert isinstance(grouped_list_result[0], list)

    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO('{"group1": {"a": "alpha"}, "group2": {"b": "beta"}}'),
    )
    grouped_dict_exit = main([command])
    grouped_dict_result = json.loads(capsys.readouterr().out)
    assert grouped_dict_exit == 0
    assert isinstance(grouped_dict_result, dict)
    assert set(grouped_dict_result.keys()) == {"group1", "group2"}


def test_batch_performance_sanity(monkeypatch, capsys):
    """Analyze command handles moderate batch size within a sanity threshold."""
    payload = json.dumps([f"content item {index}" for index in range(250)])
    monkeypatch.setattr("sys.stdin", io.StringIO(payload))

    start = time.perf_counter()
    exit_code = main(["analyze"])
    elapsed = time.perf_counter() - start

    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert isinstance(result, list)
    assert len(result) == 250
    assert elapsed < 2.0
