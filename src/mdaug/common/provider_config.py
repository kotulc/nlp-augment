"""Provider configuration loading for registry/factory selection."""

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


def load_provider_settings(
    config_path: str | Path | None = None,
    environ: dict[str, str] | None = None,
) -> ProviderSettings:
    """Load provider settings from config.yaml with environment overrides."""
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    env = environ if environ is not None else os.environ

    providers_config: dict[str, object] = {}
    if path.exists():
        parsed = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(parsed, dict):
            providers_section = parsed.get("providers", {})
            if isinstance(providers_section, dict):
                providers_config = providers_section

    analysis = env.get("MDAUG_PROVIDER_ANALYSIS", providers_config.get("analysis", "mock"))
    extraction = env.get("MDAUG_PROVIDER_EXTRACTION", providers_config.get("extraction", "mock"))
    generative = env.get("MDAUG_PROVIDER_GENERATIVE", providers_config.get("generative", "mock"))
    relevance = env.get("MDAUG_PROVIDER_RELEVANCE", providers_config.get("relevance", "mock"))

    return ProviderSettings(
        analysis=_as_provider_name(analysis, "analysis"),
        extraction=_as_provider_name(extraction, "extraction"),
        generative=_as_provider_name(generative, "generative"),
        relevance=_as_provider_name(relevance, "relevance"),
    )
