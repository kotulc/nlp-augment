import pytest
from app.settings import get_settings

@pytest.fixture(autouse=True)
def enable_debug_models(monkeypatch):
    """Enable debug models by default for all tests; tests may override with monkeypatch."""
    settings = get_settings()
    # ensure the canonical settings object has debug=True
    monkeypatch.setattr(settings, "debug", True, raising=False)
    # also ensure modules that imported a module-level settings variable see the change
    monkeypatch.setattr(loader, "settings", settings, raising=False)
    yield