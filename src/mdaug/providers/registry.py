"""Simple provider registry used during early refactor phases."""

from collections.abc import Callable


class ProviderRegistry:
    """Store provider factories keyed by role and provider name."""

    def __init__(self) -> None:
        self._factories: dict[str, dict[str, Callable]] = {}

    def register(self, role: str, name: str, factory: Callable) -> None:
        """Register a provider factory for a specific provider role."""
        if role not in self._factories:
            self._factories[role] = {}
        self._factories[role][name] = factory

    def resolve(self, role: str, name: str) -> Callable:
        """Resolve a provider factory by role and name."""
        if role not in self._factories:
            raise KeyError(f"Provider role is not registered: {role}")
        if name not in self._factories[role]:
            raise KeyError(f"Provider is not registered for role '{role}': {name}")

        return self._factories[role][name]
