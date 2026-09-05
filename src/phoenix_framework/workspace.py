"""Unified authorized module workspace discovery."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from phoenix_framework.capabilities.discovery import discover_capabilities
from phoenix_framework.capabilities.registry import CapabilityRegistry
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleIntegrationContract, NavigationContract
from phoenix_framework.dependencies import validate_dependencies
from phoenix_framework.discovery import discover_modules, discover_navigation
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


@dataclass(frozen=True)
class ModuleWorkspace:
    """Authorized, Core-context-aware projection of a module workspace."""

    module: ModuleContract
    navigation: Tuple[NavigationContract, ...] = ()
    capabilities: Tuple[str, ...] = ()


def discover_module_workspaces(
    module_registry: ModuleRegistry,
    navigation_registry: NavigationRegistry,
    capability_registry: CapabilityRegistry,
    context: FrameworkContext,
    integration_contracts: Tuple[ModuleIntegrationContract, ...] = (),
) -> List[ModuleWorkspace]:
    """Build authorized module workspace projections from Framework registries."""
    if integration_contracts:
        issues = validate_dependencies(integration_contracts)
        blocked = {issue.module_code for issue in issues if issue.reason != "missing optional module"}
    else:
        blocked = set()

    modules = [
        module for module in discover_modules(module_registry, context)
        if module.code not in blocked
    ]
    navigation = discover_navigation(navigation_registry, context)
    capabilities = discover_capabilities(capability_registry, context)

    navigation_by_module = {}
    for item in navigation:
        if item.module_code:
            navigation_by_module.setdefault(item.module_code, []).append(item)

    available_capabilities = {item.capability.code for item in capabilities}

    workspaces = []
    for module in modules:
        module_capabilities = tuple(
            capability for capability in module.capabilities
            if capability in available_capabilities
        )
        workspaces.append(
            ModuleWorkspace(
                module=module,
                navigation=tuple(navigation_by_module.get(module.code, ())),
                capabilities=module_capabilities,
            )
        )
    return workspaces
