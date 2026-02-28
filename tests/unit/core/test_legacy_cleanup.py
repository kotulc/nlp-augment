"""Unit tests that guard against legacy runtime import paths."""

from pathlib import Path


def test_no_legacy_imports_in_provider_runtime_modules():
    """Active provider runtime modules do not reference legacy import paths."""
    provider_paths = [
        Path("src/mdaug/providers/factory.py"),
        Path("src/mdaug/providers/interfaces.py"),
        Path("src/mdaug/providers/mock.py"),
        Path("src/mdaug/providers/registry.py"),
    ]
    legacy_markers = ("app.", "src.models.", "src.core.")

    for path in provider_paths:
        text = path.read_text(encoding="utf-8")
        assert all(marker not in text for marker in legacy_markers)
