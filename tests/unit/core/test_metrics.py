"""Unit tests for request normalization and output mirroring."""

import pytest

from mdaug.schemas.errors import RequestValidationError
from mdaug.schemas.io import map_results, normalize_request


@pytest.mark.parametrize(
    "payload, expected",
    [
        (["content"], "list"),
        ({"id1": "content"}, "dict"),
        ([["a"], ["b"]], "grouped_list"),
        ([{"id1": "a"}, {"id2": "b"}], "grouped_list"),
        ({"group1": {"id1": "a"}}, "grouped_dict"),
        ({"group1": ["a", "b"]}, "grouped_dict"),
    ],
)
def test_normalize_request_valid_shapes(payload, expected):
    """Supported payload shapes normalize with expected top-level shape labels."""
    request = normalize_request(payload)
    assert request.shape == expected


@pytest.mark.parametrize(
    "payload",
    [
        None,
        42,
        ["ok", 1],
        [{"id1": "a"}, ["b"]],
        {"id1": 10},
        {"group1": {"id1": "a"}, "group2": 2},
        {"group1": ["a", 2]},
    ],
)
def test_normalize_request_invalid_shapes(payload):
    """Invalid payload shapes raise RequestValidationError."""
    with pytest.raises(RequestValidationError):
        normalize_request(payload)


def test_map_results_mirrors_grouped_dict_shape():
    """Mapped results preserve grouped dictionary request structure."""
    request = normalize_request(
        {
            "group1": {"id1": "alpha"},
            "group2": {"id2": "beta"},
        }
    )
    result = map_results(
        request,
        item_mapper=lambda item_id, _: {"id": item_id, "status": "ok"},
    )

    assert set(result.keys()) == {"group1", "group2"}
    assert result["group1"]["id1"]["id"] == "id1"
    assert result["group2"]["id2"]["status"] == "ok"


def test_map_results_mirrors_grouped_list_shape():
    """Mapped results preserve grouped list request structure."""
    request = normalize_request([["a", "b"], ["c"]])
    result = map_results(
        request,
        item_mapper=lambda item_id, content: {"id": item_id, "content": content},
    )

    assert isinstance(result, list)
    assert isinstance(result[0], list)
    assert result[0][0]["content"] == "a"
    assert result[1][0]["content"] == "c"
