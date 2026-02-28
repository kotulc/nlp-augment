"""Unit tests for payload shape classification."""

import pytest

from mdaug.schemas.io import get_payload_type


@pytest.mark.parametrize(
    "payload, expected",
    [
        (None, "empty"),
        ([], "list"),
        (["content"], "list"),
        ({}, "dict"),
        ({"id1": "content"}, "dict"),
        ([["a"], ["b"]], "grouped_list"),
        ([{"id1": "a"}, {"id2": "b"}], "grouped_dict_list"),
        ({"group1": {"id1": "a"}}, "grouped_dict"),
    ],
)
def test_get_payload_type(payload, expected):
    """Each supported request shape maps to the expected payload type label."""
    assert get_payload_type(payload) == expected


def test_get_payload_type_unknown():
    """Unknown payload objects map to their type name."""
    assert get_payload_type(42) == "int"
