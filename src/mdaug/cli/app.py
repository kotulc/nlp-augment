"""CLI entrypoint with phase-1 command stubs and JSON I/O plumbing."""

import argparse
import json
import sys
from pathlib import Path

from mdaug.cli.commands import COMMANDS
from mdaug.schemas.errors import RequestValidationError, to_error_payload
from mdaug.schemas.io import normalize_request
from mdaug.service.runtime import run_command


def build_parser() -> argparse.ArgumentParser:
    """Build the mdaug command parser."""
    parser = argparse.ArgumentParser(prog="mdaug")
    subparsers = parser.add_subparsers(dest="command")

    for command in COMMANDS:
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--file", dest="file_path")
        command_parser.add_argument("--out", dest="out_path")

    return parser


def _read_payload(file_path: str | None) -> object:
    """Read JSON payload from --file or stdin."""
    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))

    stdin = sys.stdin
    if hasattr(stdin, "isatty") and stdin.isatty():
        return None

    raw_text = stdin.read()
    if not raw_text.strip():
        return None

    return json.loads(raw_text)


def _write_result(result: object, out_path: str | None) -> None:
    """Write JSON result to stdout or --out file."""
    text = json.dumps(result, indent=2)
    if out_path:
        Path(out_path).write_text(text + "\n", encoding="utf-8")
        return

    sys.stdout.write(text + "\n")


def main(argv: list[str] | None = None) -> int:
    """Execute a CLI command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    try:
        payload = _read_payload(args.file_path)
    except FileNotFoundError:
        _write_result(
            to_error_payload("invalid_input", f"File not found: {args.file_path}"),
            args.out_path,
        )
        return 1
    except json.JSONDecodeError as exc:
        _write_result(to_error_payload("invalid_json", str(exc)), args.out_path)
        return 1

    try:
        request = normalize_request(payload)
    except RequestValidationError as exc:
        _write_result(to_error_payload(exc.code, exc.message), args.out_path)
        return 1

    result = run_command(args.command, request)
    _write_result(result, args.out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
