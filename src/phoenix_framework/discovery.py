"""Core-authoritative discovery for Framework modules and navigation."""

from __future__ import annotations

from typing import List

from phoenix_framework.context.framework import FrameworkContext
from phoenix_framework.contracts import ModuleContract, NavigationContract
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


def _module_available(module: ModuleContract, context: FrameworkContext) -> bool:
    """Return whether Core-provided context permits module discovery."""
    if not module.enabled:
        return False
    return all(context.has_permission(p) for p in module.required_permissions) and all(
        context.has_entitlement(e) for e in module.required_entitlements
    )


def discover_modules(
    module_registry: ModuleRegistry,
    context: FrameworkContext,
) -> List[ModuleContract]:
    """Return modules available to the current Core security context."""
    return [module for module in module_registry.list() if _module_available(module, context)]


def navigation_available(item: NavigationContract, context: FrameworkContext) -> bool:
    """Return whether Core-provided context permits navigation exposure."""
    if not item.enabled:
        return False
    if item.permission and not context.has_permission(item.permission):
        return False
    if item.entitlement and not context.has_entitlement(item.entitlement):
        return False
    return True


def discover_navigation(
    navigation_registry: NavigationRegistry,
    context: FrameworkContext,
) -> List[NavigationContract]:
    """Return navigation contributions available to the current Core context."""
    return [item for item in navigation_registry.list() if navigation_available(item, context)]
