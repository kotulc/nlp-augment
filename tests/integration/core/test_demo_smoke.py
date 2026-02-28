"""Integration smoke tests for legacy core demo functions."""

import importlib

import pytest


DEMO_TARGETS = (
    ("mdaug.core.analysis.polarity", "demo_polarity"),
    ("mdaug.core.analysis.sentiment", "demo_sentiment"),
    ("mdaug.core.analysis.spam", "demo_spam"),
    ("mdaug.core.analysis.style", "demo_style"),
    ("mdaug.core.extraction.extract", "demo_tagger"),
    ("mdaug.core.generation.generate", "demo_generator"),
    ("mdaug.core.generation.headings", "demo_headings"),
)


@pytest.mark.parametrize("module_name,function_name", DEMO_TARGETS)
def test_demo_function_runs_without_error(module_name: str, function_name: str):
    """Run each available demo function and ensure it completes without raising."""
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        pytest.skip(f"Legacy dependency not available yet: {exc}")

    demo_function = getattr(module, function_name)
    demo_function()
