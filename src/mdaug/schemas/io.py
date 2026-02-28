"""Input/output shape classification helpers for CLI requests."""


def get_payload_type(payload: object) -> str:
    """Return a simple classifier label for a payload shape."""
    if payload is None:
        return "empty"

    if isinstance(payload, list):
        if not payload:
            return "list"

        first_item = payload[0]
        if isinstance(first_item, list):
            return "grouped_list"
        if isinstance(first_item, dict):
            return "grouped_dict_list"
        return "list"

    if isinstance(payload, dict):
        if not payload:
            return "dict"

        first_value = next(iter(payload.values()))
        if isinstance(first_value, dict):
            return "grouped_dict"
        return "dict"

    return type(payload).__name__
