"""Unit tests that guard against legacy runtime import paths."""

import importlib
from pathlib import Path


def test_no_legacy_imports_in_provider_runtime_modules():
    """Active provider runtime modules do not reference legacy import paths."""
    provider_paths = [
        Path("src/mdaug/providers/factory.py"),
        Path("src/mdaug/providers/interfaces.py"),
        Path("src/mdaug/providers/mock.py"),
        Path("src/mdaug/providers/registry.py"),
        Path("src/mdaug/core/relevance/relevance.py"),
    ]
    legacy_markers = ("app.", "src.models.", "src.core.")

    for path in provider_paths:
        text = path.read_text(encoding="utf-8")
        assert all(marker not in text for marker in legacy_markers)


def test_relevance_module_imports_without_legacy_model_paths():
    """Relevance helper module imports without requiring removed legacy packages."""
    importlib.import_module("mdaug.core.relevance.relevance")
