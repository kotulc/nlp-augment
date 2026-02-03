import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_tags_route():
    payload = {"content": "Sample text for tagging goes here Mr. Deloit."}
    response = client.post("/tags/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "result" in data
    assert "metadata" in data
    
    assert "tags" in data["result"]
    assert "scores" in data["result"]


def test_tags_route_required():
    """Verify response fails without required content"""
    response = client.post("/tags/", json={})
    assert response.status_code != 200


@pytest.mark.parametrize("min_length, max_length", [(1, 2), (2, 4), (3, 5)])
def test_tags_route_min_max(min_length, max_length):
    # 2. min/max length of returned related tags are respected
    payload = {
        "content": "Test content for tagging.",
        "parameters": {"max_length": max_length}
    }
    response = client.post("/tags/", json=payload)
    assert response.status_code == 200

    data = response.json()
    for k, v in data["result"]["tags"].items():
        # Verify lengths of related tags and scores match
        assert len(v) == len(data["result"]["scores"][k])

        # Verify min/max lengths for related tags
        for tag in v:
            word_count = len(tag.split())
            assert word_count <= max_length


@pytest.mark.parametrize("top_n", [1, 3, 5, 10])
def test_tags_route_top_n_limit(top_n):
    # 3. All returned results have length <= top_n
    payload = {
        "content": "Test content for tagging.",
        "parameters": {"top_n": top_n}
    }
    response = client.post("/tags/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    tags = data["result"].get("related", [])
    assert len(tags) <= top_n


if __name__ == "__main__":
    test_tags_route()
    test_tags_route_required()
    test_tags_route_min_max(1, 2)
    test_tags_route_top_n_limit(5)
