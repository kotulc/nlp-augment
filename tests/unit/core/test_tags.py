import pytest

from app.core.operations import get_tags, TAG_TYPES


def test_tags():
    """Verify only 'content' argument is required"""
    results = get_tags(content="Sample text for tagging goes here Mr. Deloit.")
    assert isinstance(results, dict)

    for tag_type in TAG_TYPES.keys():
        assert tag_type in results["tags"]
        assert tag_type in results["scores"]


@pytest.mark.parametrize("min_length, max_length", [(1, 2), (2, 4), (3, 5)])
def test_tags_min_max(min_length, max_length):
    """Test min and max length constraints for 'related' tags"""
    results = get_tags(
        content="Test content for tagging. This is sample data to generate tags.",
        min_length=min_length,
        max_length=max_length,
    )
    for tag in results["tags"]["related"]:
        word_count = len(tag.split())
        assert min_length <= word_count <= max_length


@pytest.mark.parametrize("top_n", [1, 3, 5])
def test_tags_top_n_limit(top_n):
    """Test top_n limit for each tag type"""
    results = get_tags(
        content="Test content for tagging. This is sample data to generate tags.",
        top_n=top_n,
    )

    # Verify tags length is less than or equal to top_n
    for k, v in results['tags'].items():
        assert len(v) <= top_n

    # Verify scores length matches tags length
    for k, v in results['scores'].items():
        assert len(v) <= top_n
        assert len(v) == len(results['tags'][k])
