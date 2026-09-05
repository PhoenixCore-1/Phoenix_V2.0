"""Generic external-module registration boundary for Phoenix Framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from phoenix_framework.contracts import (
    ModuleContract,
    ModuleIntegrationContract,
    NavigationContract,
)
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


@dataclass(frozen=True)
class ModuleRegistrationBundle:
    """Contracts supplied by an external business module."""

    module: ModuleContract
    integration: ModuleIntegrationContract
    navigation: Tuple[NavigationContract, ...] = ()


def register_module(
    bundle: ModuleRegistrationBundle,
    module_registry: ModuleRegistry,
    navigation_registry: NavigationRegistry,
) -> None:
    """Register an external module without creating a Core-to-module dependency."""
    if bundle.module.code != bundle.integration.module_code:
        raise ValueError("Module and integration contract codes must match")
    if bundle.module.version != bundle.integration.version:
        raise ValueError("Module and integration contract versions must match")
    if module_registry.has(bundle.module.code):
        raise ValueError(f"Module already registered: {bundle.module.code}")

    seen_navigation = set()
    for navigation in bundle.navigation:
        if navigation.module_code != bundle.module.code:
            raise ValueError("Navigation contract belongs to a different module")
        if navigation.key in seen_navigation or navigation_registry.has(navigation.key):
            raise ValueError(f"Navigation already registered: {navigation.key}")
        seen_navigation.add(navigation.key)

    # All validation occurs before mutation so registration is atomic.
    module_registry.register(bundle.module)
    for navigation in bundle.navigation:
        navigation_registry.register(navigation)
