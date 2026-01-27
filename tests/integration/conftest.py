import pytest


@pytest.fixture(autouse=True)
def mock_all_operations(mocker):
    """Enable debug models by default for all tests; tests may override with monkeypatch."""
    mocked_func = mocker.patch("app.core.operations.get_result", return_value="new_value")
    yield
