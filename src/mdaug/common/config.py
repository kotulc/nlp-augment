"""Common configuration entrypoints for runtime settings."""

from functools import lru_cache
from pathlib import Path

from mdaug.common.provider_config import ProviderSettings, load_provider_settings


@lru_cache(maxsize=1)
def get_provider_settings(
    config_path: str | Path | None = None,
    overrides: dict[str, str] | None = None,
) -> ProviderSettings:
    """Load cached provider settings with CLI/environment/config precedence."""
    return load_provider_settings(config_path=config_path, overrides=overrides)
