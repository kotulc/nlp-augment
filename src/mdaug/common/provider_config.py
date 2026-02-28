"""Provider configuration loading with deterministic precedence rules."""

from dataclasses import dataclass
from pathlib import Path
import os

import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")


@dataclass(frozen=True)
class ProviderSettings:
    """Provider selection names for each provider role."""

    analysis: str = "mock"
    extraction: str = "mock"
    generative: str = "mock"
    relevance: str = "mock"


def _as_provider_name(value: object, field_name: str) -> str:
    """Validate and normalize a provider name value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Provider setting '{field_name}' must be a non-empty string.")

    return value.strip()


def _validated_provider_map(values: dict[str, object]) -> dict[str, str]:
    """Validate and normalize provider mapping values."""
    return {
        "analysis": _as_provider_name(values.get("analysis", "mock"), "analysis"),
        "extraction": _as_provider_name(values.get("extraction", "mock"), "extraction"),
        "generative": _as_provider_name(values.get("generative", "mock"), "generative"),
        "relevance": _as_provider_name(values.get("relevance", "mock"), "relevance"),
    }


def load_provider_settings(
    config_path: str | Path | None = None,
    environ: dict[str, str] | None = None,
    overrides: dict[str, str] | None = None,
) -> ProviderSettings:
    """Load provider settings with precedence: CLI > env > config > default."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    env = environ if environ is not None else os.environ
    cli_overrides = overrides or {}

    merged = {
        "analysis": "mock",
        "extraction": "mock",
        "generative": "mock",
        "relevance": "mock",
    }

    if path.exists():
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(parsed, dict):
            providers_section = parsed.get("providers", {})
            if isinstance(providers_section, dict):
                merged.update(providers_section)

    env_values = {
        "analysis": env.get("MDAUG_PROVIDER_ANALYSIS"),
        "extraction": env.get("MDAUG_PROVIDER_EXTRACTION"),
        "generative": env.get("MDAUG_PROVIDER_GENERATIVE"),
        "relevance": env.get("MDAUG_PROVIDER_RELEVANCE"),
    }
    merged.update({key: value for key, value in env_values.items() if value})

    merged.update({key: value for key, value in cli_overrides.items() if value})
    validated = _validated_provider_map(merged)
    return ProviderSettings(**validated)
