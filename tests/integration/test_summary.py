import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.operations import SUMMARY_TYPES


client = TestClient(app)


def test_summary():
    """Only 'content' is required"""
    payload = {"content": "Test content for summary."}
    response = client.post("/summary/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "summaries" in data["result"]
    assert "scores" in data["result"]
    assert len(data["result"]["summaries"])
    assert len(data["result"]["summaries"]) == len(data["result"]["scores"])


@pytest.mark.parametrize("summary_type", list(SUMMARY_TYPES.keys()))
def test_summary_type(summary_type):
    """Test each summary type individually"""
    payload = {
        "content": "Test content for summary.",
        "summary": summary_type
    }
    response = client.post("/summary/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "result" in data
    assert "summaries" in data["result"]
    assert len(data["result"]["summaries"])


@pytest.mark.parametrize("summary_type", list(SUMMARY_TYPES.keys()))
def test_summary_routes(summary_type):
    """Test each summary type individually"""
    payload = {"content": "Test content for summary."}
    response = client.post(f"/summary/{summary_type}/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "result" in data
    assert "summaries" in data["result"]
    assert len(data["result"]["summaries"])


@pytest.mark.parametrize("top_n", [1, 3, 5])
def test_summary_top_n(top_n):
    """All returned results have length <= top_n"""
    payload = {
        "content": "Test content for summary.",
        "summary": "description",
        "top_n": top_n
    }
    response = client.post("/summary/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "result" in data
    assert "summaries" in data["result"]
    assert len(data["result"]["summaries"]) <= top_n


if __name__ == "__main__":
    test_summary()
    test_summary_type("outline")
    test_summary_top_n(top_n=5)
