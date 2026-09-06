"""Presentation adapter for the Phoenix Generic Framework navigation registry."""

from collections.abc import Iterable

from phoenix_framework.contracts import NavigationContract
from phoenix_framework.navigation.registry import NavigationRegistry


def visible_navigation(registry: NavigationRegistry) -> list[NavigationContract]:
    """Return enabled navigation contributions for presentation.

    Authorization and entitlements are deliberately not evaluated here;
    Phoenix Core remains authoritative for those decisions.
    """
    return [item for item in registry.list() if item.enabled]


def register_default_navigation(registry: NavigationRegistry) -> None:
    """Register only platform-level navigation owned by the system shell."""
    defaults: Iterable[NavigationContract] = (
        NavigationContract(
            key="system.dashboard",
            label="Dashboard",
            route="/",
            order=0,
        ),
        NavigationContract(
            key="system.administration",
            label="System",
            route="/system",
            order=900,
        ),
    )
    for item in defaults:
        if not registry.has(item.key):
            registry.register(item)
