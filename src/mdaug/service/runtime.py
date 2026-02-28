"""Runtime orchestration for command routing."""

from mdaug.cli.commands import COMMANDS
from mdaug.core.operations import GROUP_COMMANDS, ITEM_COMMANDS, run_group_operation, run_item_operation
from mdaug.providers.factory import ProviderBundle, get_provider_bundle
from mdaug.schemas.io import NormalizedRequest, map_results


def run_command(
    command: str,
    request: NormalizedRequest,
    providers: ProviderBundle | None = None,
) -> dict | list:
    """Run a command stub and return a result mirrored to request shape."""
    if command not in COMMANDS:
        return {"error": "invalid_command", "message": f"Unsupported command: {command}"}

    provider_bundle = providers if providers is not None else get_provider_bundle()
    if command in ITEM_COMMANDS:
        return map_results(
            request=request,
            item_mapper=lambda _item_id, content: run_item_operation(
                command=command,
                content=content,
                providers=provider_bundle,
            ),
        )

    if command in GROUP_COMMANDS:
        group_outputs: list[dict] = []
        for group in request.groups:
            group_outputs.append(
                run_group_operation(
                    command=command,
                    group=group,
                    providers=provider_bundle,
                )
            )

        if request.shape in {"list", "dict"}:
            return group_outputs[0]
        if request.shape == "grouped_list":
            return group_outputs
        return {
            group_id: group_output
            for group_id, group_output in zip(request.group_ids or [], group_outputs)
        }

    return {"error": "invalid_command", "message": f"Unsupported command: {command}"}
