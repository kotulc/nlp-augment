import pytest

from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.operations import METRIC_KEYS, METRIC_TYPES, SENTIMENT_KEYS
from app.core.metrics.style import DICTION_LABELS, GENRE_LABELS, MODE_LABELS, TONE_LABELS


@pytest.fixture
def sample_metric_request(sample_section_id: str) -> dict:
    """Return a sample metric request payload"""
    return dict(section_id=sample_section_id, content="Test content for metrics", metrics=None)


@pytest.fixture
def sample_section_id() -> str:
    """Provide a consistent section UUID for tests"""
    return str(uuid4())


def test_metrics_route(test_client: TestClient, sample_metric_request: dict):
    """Verify a standard request returns the expected response"""
    response = test_client.post("/metrics/", json=sample_metric_request)
    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == len(METRIC_KEYS)
    assert set(data["results"].keys()) == METRIC_KEYS
    assert all(isinstance(value, float) for value in data["results"].values())


@pytest.mark.parametrize("metric_type", [m for m in METRIC_TYPES.keys()])
def test_metrics_route_single_type(test_client: TestClient, sample_metric_request: dict, metric_type: str):
    """Test each metric type individually"""
    sample_metric_request["metrics"] = [metric_type]
    response = test_client.post("/metrics/", json=sample_metric_request)
    assert response.status_code == 200

    # Results should contain the metric keys of the requested metric type
    expected_keys = set()
    match metric_type:
        case "diction":
            expected_keys = set(DICTION_LABELS)
        case "genre":
            expected_keys = set(GENRE_LABELS)
        case "mode":
            expected_keys = set(MODE_LABELS)
        case "tone":
            expected_keys = set(TONE_LABELS)
        case "sentiment":
            expected_keys = SENTIMENT_KEYS
        case "polarity" | "toxicity" | "spam":
            expected_keys = {metric_type}

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == len(expected_keys)
    assert set(data["results"].keys()) == expected_keys
    assert all(isinstance(value, float) for value in data["results"].values())


@pytest.mark.parametrize("metric_types", [
    [m for m in METRIC_TYPES],
    [m for m in METRIC_TYPES][:2],
])
def test_metrics_route_multiple_types(test_client: TestClient, sample_metric_request: dict, metric_types: str):
    """Test multiple metric types at once"""
    sample_metric_request["metrics"] = metric_types
    response = test_client.post("/metrics/", json=sample_metric_request)
    assert response.status_code == 200

    # Results should contain the metric keys of the requested metric type
    expected_keys = []
    for metric_type in metric_types:
        match metric_type:
            case "diction":
                expected_keys.extend(DICTION_LABELS)
            case "genre":
                expected_keys.extend(GENRE_LABELS)
            case "mode":
                expected_keys.extend(MODE_LABELS)
            case "tone":
                expected_keys.extend(TONE_LABELS)
            case "sentiment":
                expected_keys.extend(SENTIMENT_KEYS)
            case "polarity" | "toxicity" | "spam":
                expected_keys.append(metric_type)

    data = response.json()
    assert "results" in data
    assert len(data["results"]) == len(set(expected_keys))
    assert set(data["results"].keys()) == set(expected_keys)
    assert all(isinstance(value, float) for value in data["results"].values())
