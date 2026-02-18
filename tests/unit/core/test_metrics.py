import pytest

from app.core.operations import get_metrics, METRIC_TYPES


def test_metrics():
    """Confirm only 'content' argument is required"""
    results = compute_metrics(content="Test content for metrics.")
    for metric in METRIC_TYPES.keys():
        assert metric in results


@pytest.mark.parametrize("metric_type", [m for m in METRIC_TYPES])
def test_metrics_single_type(metric_type: str):
    """Test each metric type individually"""
    results = compute_metrics(content="Test content for metrics.", metrics=[metric_type])
    for metric in METRIC_TYPES.keys():
        if metric != metric_type:
            assert not metric in results
        else:
            assert metric in results
            assert isinstance(results[metric], dict)
            assert len(results[metric]) > 0


@pytest.mark.parametrize("metric_types", [
    [m for m in METRIC_TYPES],
    [m for m in METRIC_TYPES][:2],
])
def test_metrics_multiple_types(metric_types: list):
    """Test multiple metric types at once"""
    results = compute_metrics(content="Test content for metrics.", metrics=metric_types)
    for metric in metric_types:
        assert metric in results
        assert isinstance(results[metric], dict)
        assert len(results[metric]) > 0
