"""CLI entrypoint with normalized JSON input and output contract handling."""

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


def _log_error(message: str) -> None:
    """Write diagnostic error details to stderr."""
    sys.stderr.write(message + "\n")


def _emit_error(error: str, message: str, out_path: str | None) -> None:
    """Emit an error payload, falling back to stdout if file output fails."""
    payload = to_error_payload(error, message)
    try:
        _write_result(payload, out_path)
    except OSError as exc:
        _write_result(payload, None)
        _log_error(f"Failed writing output to '{out_path}': {exc}")


def _read_payload(file_path: str | None) -> object:
    """Read JSON payload from exactly one source: --file or stdin."""
    stdin = sys.stdin
    raw_stdin = ""
    if not (hasattr(stdin, "isatty") and stdin.isatty()):
        try:
            raw_stdin = stdin.read()
        except OSError:
            raw_stdin = ""

    has_stdin_input = bool(raw_stdin.strip())
    if file_path and has_stdin_input:
        raise RequestValidationError(
            "invalid_input_source",
            "Provide input from either stdin or --file, not both.",
        )

    if file_path:
        return json.loads(Path(file_path).read_text(encoding="utf-8"))

    if not has_stdin_input:
        return None

    return json.loads(raw_stdin)


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
        _emit_error("invalid_input", f"File not found: {args.file_path}", args.out_path)
        return 1
    except RequestValidationError as exc:
        _emit_error(exc.code, exc.message, args.out_path)
        return 1
    except json.JSONDecodeError as exc:
        _emit_error("invalid_json", str(exc), args.out_path)
        return 1

    try:
        request = normalize_request(payload)
    except RequestValidationError as exc:
        _emit_error(exc.code, exc.message, args.out_path)
        return 1

    result = run_command(args.command, request)
    try:
        _write_result(result, args.out_path)
    except OSError as exc:
        _emit_error("invalid_output", str(exc), args.out_path)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
