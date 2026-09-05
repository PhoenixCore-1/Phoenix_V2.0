"""Core-context-aware capability discovery."""

from __future__ import annotations

from typing import List

from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts.capability import PlatformCapabilityContract
from phoenix_framework.capabilities.registry import CapabilityRegistry


def capability_available(
    capability: PlatformCapabilityContract,
    context: FrameworkContext,
) -> bool:
    """Return whether Core-provided context authorizes capability use."""
    metadata = capability.capability
    if not metadata.enabled:
        return False
    if not all(context.has_permission(p) for p in capability.required_permissions()):
        return False
    if not all(context.has_entitlement(e) for e in capability.required_entitlements()):
        return False
    return capability.is_available(context)


def discover_capabilities(
    registry: CapabilityRegistry,
    context: FrameworkContext,
) -> List[PlatformCapabilityContract]:
    """Return capabilities available to the current Core security context."""
    return [
        capability
        for capability in registry.list()
        if capability_available(capability, context)
    ]
