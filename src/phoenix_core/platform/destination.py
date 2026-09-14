"""Authoritative Phoenix platform destination resolution."""

from dataclasses import dataclass
from typing import FrozenSet

from phoenix_core.security.context import RequestContext


@dataclass(frozen=True)
class PlatformDestination:
    """A destination exposed by the authenticated Phoenix session."""

    code: str
    path: str
    label: str


SYSTEM_PERMISSION_PREFIXES = ("system.", "platform.")

DESTINATIONS = (
    PlatformDestination("system", "/system", "System Platform"),
    PlatformDestination("company", "/company", "Company Platform"),
    PlatformDestination("user", "/user", "User Platform"),
)


def resolve_destinations(context: RequestContext) -> FrozenSet[str]:
    """Resolve allowed top-level destinations from authoritative Core context.

    The browser supplies no destination authority. Core permissions determine
    platform-level access; an authenticated tenant member may enter the User
    Platform, while Company Platform requires an existing company permission.
    """
    permissions = context.permissions
    destinations: set[str] = {"user"}

    if any(
        permission.startswith(prefix)
        for permission in permissions
        for prefix in SYSTEM_PERMISSION_PREFIXES
    ):
        destinations.add("system")

    if any(permission.startswith("company.") for permission in permissions):
        destinations.add("company")

    return frozenset(destinations)


def destination_payload(context: RequestContext) -> dict:
    allowed = resolve_destinations(context)
    return {
        "destinations": [
            {"code": item.code, "path": item.path, "label": item.label}
            for item in DESTINATIONS
            if item.code in allowed
        ],
        "default": "company" if "company" in allowed else "system" if "system" in allowed else "user",
    }
