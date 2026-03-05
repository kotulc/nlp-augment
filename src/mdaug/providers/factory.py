"""Provider factory and default registry construction."""

from dataclasses import dataclass
from functools import lru_cache

from mdaug.common.provider_config import ProviderSettings, load_provider_settings
from mdaug.providers.interfaces import (
    AnalysisProvider,
    ExtractionProvider,
    GenerativeProvider,
    RelevanceProvider,
)
from mdaug.providers.default.provider import (
    DefaultAnalysisProvider,
    DefaultExtractionProvider,
    DefaultGenerativeProvider,
    DefaultRelevanceProvider,
)
from mdaug.providers.registry import ProviderRegistry


@dataclass(frozen=True)
class ProviderBundle:
    """Concrete provider instances selected by provider settings."""

    analysis: AnalysisProvider
    extraction: ExtractionProvider
    generative: GenerativeProvider
    relevance: RelevanceProvider
    names: ProviderSettings


def build_default_registry() -> ProviderRegistry:
    """Build the production provider registry with default provider implementations."""
    registry = ProviderRegistry()
    registry.register("analysis", "default", DefaultAnalysisProvider)
    registry.register("extraction", "default", DefaultExtractionProvider)
    registry.register("generative", "default", DefaultGenerativeProvider)
    registry.register("relevance", "default", DefaultRelevanceProvider)
    return registry


def create_provider_bundle(
    settings: ProviderSettings,
    registry: ProviderRegistry | None = None,
    ) -> ProviderBundle:
    """Create a provider bundle from settings and a provider registry."""
    provider_registry = registry if registry is not None else build_default_registry()

    analysis_factory = provider_registry.resolve("analysis", settings.analysis)
    extraction_factory = provider_registry.resolve("extraction", settings.extraction)
    generative_factory = provider_registry.resolve("generative", settings.generative)
    relevance_factory = provider_registry.resolve("relevance", settings.relevance)

    return ProviderBundle(
        analysis=analysis_factory(),
        extraction=extraction_factory(),
        generative=generative_factory(),
        relevance=relevance_factory(),
        names=settings,
    )


def build_provider_bundle(
    config_path: str | None = None,
    registry: ProviderRegistry | None = None,
    ) -> ProviderBundle:
    """Build a provider bundle using config.yaml provider settings."""
    settings = load_provider_settings(config_path=config_path)
    return create_provider_bundle(settings=settings, registry=registry)


@lru_cache(maxsize=1)
def get_provider_bundle() -> ProviderBundle:
    """Load provider settings from config and build a cached provider bundle."""
    return build_provider_bundle()
