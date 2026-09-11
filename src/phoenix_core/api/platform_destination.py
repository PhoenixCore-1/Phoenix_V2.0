"""Authoritative platform-destination contract for Phoenix Core V2."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet


class PlatformDestination(str, Enum):
    """Phoenix platform destinations resolved by Core."""

    SYSTEM_PLATFORM = "SYSTEM_PLATFORM"
    COMPANY_PLATFORM = "COMPANY_PLATFORM"
    USER_PLATFORM = "USER_PLATFORM"


# These are Core-owned authorization capabilities. They are intentionally
# defined here rather than guessed by an HTTP host or browser client.
SYSTEM_PLATFORM_ACCESS = "platform.system.access"
COMPANY_PLATFORM_ACCESS = "platform.company.access"


@dataclass(frozen=True)
class PlatformDestinationResult:
    """Authoritative destination returned after Core context resolution."""

    destination: PlatformDestination
    session_id: str
    organisation_id: str
    permissions: FrozenSet[str]
    entitlements: FrozenSet[str]
