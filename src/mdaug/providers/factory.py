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
from mdaug.providers.mock import (
    MockAnalysisProvider,
    MockExtractionProvider,
    MockGenerativeProvider,
    MockRelevanceProvider,
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
    """Build a default provider registry with deterministic mock providers."""
    registry = ProviderRegistry()
    registry.register("analysis", "mock", MockAnalysisProvider)
    registry.register("extraction", "mock", MockExtractionProvider)
    registry.register("generative", "mock", MockGenerativeProvider)
    registry.register("relevance", "mock", MockRelevanceProvider)
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


@lru_cache(maxsize=1)
def get_provider_bundle() -> ProviderBundle:
    """Load provider settings from config and build a cached provider bundle."""
    settings = load_provider_settings()
    return create_provider_bundle(settings=settings)
