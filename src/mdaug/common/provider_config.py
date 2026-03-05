"""Provider configuration loading with deterministic precedence rules."""

from dataclasses import dataclass
from pathlib import Path

import yaml


DEFAULT_CONFIG_PATH = Path("config.yaml")


@dataclass(frozen=True)
class ProviderSettings:
    """Provider selection names for each provider role."""

    analysis: str = "default"
    extraction: str = "default"
    generative: str = "default"
    relevance: str = "default"


def _as_provider_name(value: object, field_name: str) -> str:
    """Validate and normalize a provider name value."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Provider setting '{field_name}' must be a non-empty string.")

    return value.strip()


def _validated_provider_map(values: dict[str, object]) -> dict[str, str]:
    """Validate and normalize provider mapping values."""
    return {
        "analysis": _as_provider_name(values.get("analysis", "default"), "analysis"),
        "extraction": _as_provider_name(values.get("extraction", "default"), "extraction"),
        "generative": _as_provider_name(values.get("generative", "default"), "generative"),
        "relevance": _as_provider_name(values.get("relevance", "default"), "relevance"),
    }


def load_provider_settings(
    config_path: str | Path | None = None,
) -> ProviderSettings:
    """Load provider settings with precedence: config.yaml -> default."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    merged = {
        "analysis": "default",
        "extraction": "default",
        "generative": "default",
        "relevance": "default",
    }

    if path.exists():
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(parsed, dict):
            providers_section = parsed.get("providers", {})
            if isinstance(providers_section, dict):
                merged.update(providers_section)

    validated = _validated_provider_map(merged)
    return ProviderSettings(**validated)
