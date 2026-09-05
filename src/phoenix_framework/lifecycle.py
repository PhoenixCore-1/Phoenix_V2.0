"""Projection of authoritative Core module lifecycle into Framework contracts."""

from __future__ import annotations

from phoenix_core.modules.domain import Module
from phoenix_framework.contracts import ModuleLifecycle


_CORE_TO_FRAMEWORK = {
    "REGISTERED": ModuleLifecycle.REGISTERED,
    "ENABLED": ModuleLifecycle.ENABLED,
    "DISABLED": ModuleLifecycle.DISABLED,
    "RETIRED": ModuleLifecycle.DEPRECATED,
}


def framework_lifecycle(core_module: Module) -> ModuleLifecycle:
    """Project a Core-authoritative module status into Framework lifecycle."""
    try:
        return _CORE_TO_FRAMEWORK[core_module.status]
    except KeyError:
        raise ValueError(f"Unknown Core module status: {core_module.status}") from None


def is_discoverable(core_module: Module) -> bool:
    """Return whether Core lifecycle permits Framework discovery."""
    return core_module.status == "ENABLED"
