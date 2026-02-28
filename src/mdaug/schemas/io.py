"""Input normalization and output mirroring for CLI JSON payloads."""

from dataclasses import dataclass
from typing import Literal

from mdaug.schemas.errors import RequestValidationError


RequestShape = Literal["list", "dict", "grouped_list", "grouped_dict"]
GroupShape = Literal["list", "dict"]


@dataclass(frozen=True)
class RequestGroup:
    """A normalized request group with either list or dict item storage."""

    shape: GroupShape
    items: list[str] | dict[str, str]

    def iter_items(self) -> list[tuple[str | None, str]]:
        """Return normalized `(item_id, content)` tuples."""
        if self.shape == "list":
            return [(None, content) for content in self.items]

        return [(item_id, content) for item_id, content in self.items.items()]


@dataclass(frozen=True)
class NormalizedRequest:
    """Normalized request representation with top-level shape metadata."""

    shape: RequestShape
    groups: list[RequestGroup]
    group_ids: list[str] | None = None


def _validate_list_items(payload: list, prefix: str) -> list[str]:
    """Validate a list of text content strings."""
    items: list[str] = []
    for index, item in enumerate(payload):
        if not isinstance(item, str):
            raise RequestValidationError(
                "invalid_input",
                f"{prefix}[{index}] must be a string.",
            )
        items.append(item)

    return items


def _validate_dict_items(payload: dict, prefix: str) -> dict[str, str]:
    """Validate a dictionary of id-to-content string values."""
    items: dict[str, str] = {}
    for key, value in payload.items():
        if not isinstance(key, str):
            raise RequestValidationError(
                "invalid_input",
                f"{prefix} key '{key}' must be a string.",
            )
        if not isinstance(value, str):
            raise RequestValidationError(
                "invalid_input",
                f"{prefix}['{key}'] must be a string.",
            )
        items[key] = value

    return items


def _normalize_grouped_list(payload: list) -> NormalizedRequest:
    """Normalize a grouped list payload."""
    groups: list[RequestGroup] = []
    first_shape: GroupShape | None = None

    for index, group in enumerate(payload):
        if isinstance(group, list):
            shape = "list"
            items = _validate_list_items(group, f"request[{index}]")
        elif isinstance(group, dict):
            shape = "dict"
            items = _validate_dict_items(group, f"request[{index}]")
        else:
            raise RequestValidationError(
                "invalid_input",
                "Grouped list items must each be a list or dictionary.",
            )

        if first_shape is None:
            first_shape = shape
        elif first_shape != shape:
            raise RequestValidationError(
                "invalid_input",
                "Grouped list must not mix list and dictionary group types.",
            )

        groups.append(RequestGroup(shape=shape, items=items))

    return NormalizedRequest(shape="grouped_list", groups=groups)


def _normalize_grouped_dict(payload: dict) -> NormalizedRequest:
    """Normalize a grouped dictionary payload."""
    groups: list[RequestGroup] = []
    group_ids: list[str] = []

    for group_id, group in payload.items():
        if not isinstance(group_id, str):
            raise RequestValidationError(
                "invalid_input",
                f"Group key '{group_id}' must be a string.",
            )

        if isinstance(group, list):
            groups.append(
                RequestGroup(
                    shape="list",
                    items=_validate_list_items(group, f"request['{group_id}']"),
                )
            )
        elif isinstance(group, dict):
            groups.append(
                RequestGroup(
                    shape="dict",
                    items=_validate_dict_items(group, f"request['{group_id}']"),
                )
            )
        else:
            raise RequestValidationError(
                "invalid_input",
                f"request['{group_id}'] must be a list or dictionary.",
            )

        group_ids.append(group_id)

    return NormalizedRequest(shape="grouped_dict", groups=groups, group_ids=group_ids)


def normalize_request(payload: object) -> NormalizedRequest:
    """Validate and normalize a request payload."""
    if payload is None:
        raise RequestValidationError(
            "missing_input",
            "No JSON input found. Provide input via stdin or --file.",
        )

    if isinstance(payload, list):
        if not payload:
            return NormalizedRequest(shape="list", groups=[RequestGroup(shape="list", items=[])])

        if all(isinstance(item, str) for item in payload):
            items = _validate_list_items(payload, "request")
            return NormalizedRequest(shape="list", groups=[RequestGroup(shape="list", items=items)])

        if all(isinstance(item, (list, dict)) for item in payload):
            return _normalize_grouped_list(payload)

        raise RequestValidationError(
            "invalid_input",
            "Request list must contain only strings or only request groups.",
        )

    if isinstance(payload, dict):
        if not payload:
            return NormalizedRequest(shape="dict", groups=[RequestGroup(shape="dict", items={})])

        if all(isinstance(value, str) for value in payload.values()):
            items = _validate_dict_items(payload, "request")
            return NormalizedRequest(shape="dict", groups=[RequestGroup(shape="dict", items=items)])

        if all(isinstance(value, (list, dict)) for value in payload.values()):
            return _normalize_grouped_dict(payload)

        raise RequestValidationError(
            "invalid_input",
            "Request dictionary values must be strings or grouped collections.",
        )

    raise RequestValidationError(
        "invalid_input",
        "Request JSON must be a list or dictionary.",
    )


def map_results(
    request: NormalizedRequest,
    item_mapper,
):
    """Map normalized request items and return mirrored result shape."""
    group_outputs: list[list | dict] = []
    for group in request.groups:
        if group.shape == "list":
            mapped_items = [item_mapper(item_id, content) for item_id, content in group.iter_items()]
            group_outputs.append(mapped_items)
        else:
            mapped_items = {
                item_id: item_mapper(item_id, content)
                for item_id, content in group.iter_items()
            }
            group_outputs.append(mapped_items)

    if request.shape == "list":
        return group_outputs[0]
    if request.shape == "dict":
        return group_outputs[0]
    if request.shape == "grouped_list":
        return group_outputs

    return {
        group_id: group_output
        for group_id, group_output in zip(request.group_ids or [], group_outputs)
    }


def get_payload_type(payload: object) -> str:
    """Return normalized payload shape label or type name for invalid objects."""
    try:
        return normalize_request(payload).shape
    except RequestValidationError:
        return type(payload).__name__
