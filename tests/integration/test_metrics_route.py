import pytest

from fastapi.testclient import TestClient
from app.main import app
from app.core.operations import METRIC_TYPES


def test_metrics_route():
    """Confirm only 'content' argument is required"""
    payload = {"content": "Test content for metrics."}
    client = TestClient(app)
    response = client.post("/metrics/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "result" in data
    assert "metadata" in data

    for metric in METRIC_TYPES.keys():
        assert metric in data["result"]


@pytest.mark.parametrize("metric_type", [m for m in METRIC_TYPES])
def test_metrics_route_single_type(metric_type: str):
    """Test each metric type individually"""
    payload = {
        "content": "Test content for metrics.",
        "parameters": {"metrics": [metric_type]}
    }
    client = TestClient(app)
    response = client.post("/metrics/", json=payload)
    assert response.status_code == 200

    # Should contain the requested metric type in the response data
    data = response.json()
    assert "result" in data
    assert metric_type in data["result"]
    
    for metric in METRIC_TYPES.keys():
        if metric != metric_type:
            assert not metric in data["result"]


@pytest.mark.parametrize("metric_types", [
    [m for m in METRIC_TYPES],
    [m for m in METRIC_TYPES][:2],
])
def test_metrics_route_multiple_types(metric_types: list):
    """Test multiple metric types at once"""
    payload = {
        "content": "Test content for metrics.",
        "parameters": {"metrics": metric_types}
    }
    client = TestClient(app)
    response = client.post("/metrics/", json=payload)
    assert response.status_code == 200

    data = response.json()
    for metric in metric_types:
        assert metric in data["result"]
        assert isinstance(data["result"][metric], dict)


if __name__ == "__main__":
    test_metrics_route()
    test_metrics_route_single_type("diction")
    test_metrics_route_multiple_types([m for m in METRIC_TYPES][:2])
