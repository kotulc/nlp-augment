"""Simple provider registry used during early refactor phases."""

from collections.abc import Callable


class ProviderRegistry:
    """Store named provider factories."""

    def __init__(self) -> None:
        self._factories: dict[str, Callable] = {}

    def register(self, name: str, factory: Callable) -> None:
        """Register a provider factory by name."""
        self._factories[name] = factory

    def resolve(self, name: str) -> Callable:
        """Resolve a provider factory by name."""
        if name not in self._factories:
            raise KeyError(f"Provider is not registered: {name}")

        return self._factories[name]
