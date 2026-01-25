import pytest

from app.core.summary import get_summary, SUMMARY_TYPES


def test_summary():
    """Verify only 'content' argument is required"""
    results = get_summary(content="Test content for summary.", summary="description")
    assert "summaries" in results
    assert "scores" in results
    assert len(results["summaries"])
    assert len(results["summaries"]) == len(results["scores"])


@pytest.mark.parametrize("summary_type", list(SUMMARY_TYPES.keys()))
def test_summary_type(summary_type):
    """Test each summary type individually"""
    results = get_summary(content="Test content for summary.", summary=summary_type)
    assert "summaries" in results
    assert "scores" in results
    assert len(results["summaries"])
    assert len(results["summaries"]) == len(results["scores"])


@pytest.mark.parametrize("top_n", [1, 3, 5])
def test_summary_top_n(top_n):
    """All returned results have length <= top_n"""
    results = get_summary(
        content="Test content for summary.", 
        summary="description",
        top_n=top_n
    )
    assert "summaries" in results
    assert "scores" in results
    assert len(results["summaries"])
    assert len(results["summaries"]) <= top_n
