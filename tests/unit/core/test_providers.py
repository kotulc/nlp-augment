"""Unit tests for provider registry, config, and factory behavior."""

from pathlib import Path

import pytest

from mdaug.common.provider_config import ProviderSettings, load_provider_settings
from mdaug.providers.factory import build_default_registry, create_provider_bundle
from mdaug.providers.registry import ProviderRegistry


def test_provider_registry_register_and_resolve():
    """Registered provider factories resolve by role and provider name."""
    registry = ProviderRegistry()
    registry.register("analysis", "demo", lambda: {"provider": "demo"})

    factory = registry.resolve("analysis", "demo")
    assert factory() == {"provider": "demo"}


def test_provider_registry_unknown_role_or_name():
    """Resolving unknown role or provider name raises KeyError."""
    registry = ProviderRegistry()

    with pytest.raises(KeyError):
        registry.resolve("analysis", "mock")

    registry.register("analysis", "mock", object)
    with pytest.raises(KeyError):
        registry.resolve("analysis", "missing")


def test_load_provider_settings_from_config_file(tmp_path: Path):
    """Provider settings are loaded from config yaml providers section."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "providers:",
                "  analysis: mock",
                "  extraction: mock",
                "  generative: mock",
                "  relevance: mock",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_provider_settings(config_path=config_path, environ={})

    assert settings == ProviderSettings(
        analysis="mock",
        extraction="mock",
        generative="mock",
        relevance="mock",
    )


def test_load_provider_settings_env_overrides(tmp_path: Path):
    """Environment variables override config provider settings."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("providers:\n  analysis: mock\n", encoding="utf-8")
    env = {
        "MDAUG_PROVIDER_ANALYSIS": "mock",
        "MDAUG_PROVIDER_EXTRACTION": "mock",
        "MDAUG_PROVIDER_GENERATIVE": "mock",
        "MDAUG_PROVIDER_RELEVANCE": "mock",
    }

    settings = load_provider_settings(config_path=config_path, environ=env)
    assert settings.analysis == "mock"
    assert settings.extraction == "mock"
    assert settings.generative == "mock"
    assert settings.relevance == "mock"


def test_load_provider_settings_cli_overrides_env_and_config(tmp_path: Path):
    """CLI overrides take precedence over environment and config values."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "providers:",
                "  analysis: config_analysis",
                "  extraction: config_extraction",
                "  generative: config_generative",
                "  relevance: config_relevance",
            ]
        ),
        encoding="utf-8",
    )

    env = {
        "MDAUG_PROVIDER_ANALYSIS": "env_analysis",
        "MDAUG_PROVIDER_EXTRACTION": "env_extraction",
    }
    overrides = {
        "analysis": "mock",
        "extraction": "mock",
        "generative": "mock",
        "relevance": "mock",
    }

    settings = load_provider_settings(
        config_path=config_path,
        environ=env,
        overrides=overrides,
    )

    assert settings == ProviderSettings(
        analysis="mock",
        extraction="mock",
        generative="mock",
        relevance="mock",
    )


def test_load_provider_settings_falls_back_to_defaults_when_missing_config(tmp_path: Path):
    """Missing config and empty env/CLI values fall back to default provider names."""
    config_path = tmp_path / "missing.yaml"
    settings = load_provider_settings(config_path=config_path, environ={}, overrides={})

    assert settings == ProviderSettings()


def test_create_provider_bundle_with_default_registry():
    """Provider bundle creation returns deterministic mock provider selection."""
    settings = ProviderSettings()
    bundle = create_provider_bundle(settings=settings, registry=build_default_registry())

    assert bundle.names.analysis == "mock"
    assert bundle.names.extraction == "mock"
    assert bundle.names.generative == "mock"
    assert bundle.names.relevance == "mock"


def test_create_provider_bundle_unknown_provider_raises():
    """Unknown configured provider names raise KeyError during bundle creation."""
    settings = ProviderSettings(analysis="missing")

    with pytest.raises(KeyError):
        create_provider_bundle(settings=settings, registry=build_default_registry())
