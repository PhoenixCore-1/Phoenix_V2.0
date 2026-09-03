"""Stable contracts for the Phoenix Generic Framework."""

from phoenix_framework.contracts.capability import PlatformCapabilityContract
from phoenix_framework.contracts.module import ModuleContract, ModuleLifecycle
from phoenix_framework.contracts.navigation import NavigationContract
from phoenix_framework.contracts.platform import (
    CompanyContext,
    ModuleDescriptor,
    NavigationItem,
    PlatformCapability,
    UserContext,
)

__all__ = [
    "CompanyContext",
    "ModuleContract",
    "ModuleDescriptor",
    "ModuleLifecycle",
    "NavigationContract",
    "NavigationItem",
    "PlatformCapability",
    "PlatformCapabilityContract",
    "UserContext",
]
