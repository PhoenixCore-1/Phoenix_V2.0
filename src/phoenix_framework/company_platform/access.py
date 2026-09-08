"""Company Platform access and role enforcement boundary."""

from dataclasses import dataclass
from typing import Tuple

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.contracts.navigation import NavigationContract


@dataclass(frozen=True)
class CompanyCapabilityAccess:
    """Presentation-level access result derived from Core permissions."""

    capability: str
    permitted: bool


class CompanyAccessService:
    """Evaluate Company Platform access without creating authorization authority."""

    @staticmethod
    def can_access(context: CompanyPlatformContext, permission: str) -> bool:
        context.require_access()
        return context.has_permission(permission)

    @staticmethod
    def require_access(context: CompanyPlatformContext, permission: str) -> None:
        context.require_access()
        if not context.has_permission(permission):
            raise PermissionError(f"Missing required permission: {permission}")

    @staticmethod
    def evaluate_capabilities(context: CompanyPlatformContext, permissions: Tuple[str, ...]) -> Tuple[CompanyCapabilityAccess, ...]:
        context.require_access()
        return tuple(CompanyCapabilityAccess(permission, context.has_permission(permission)) for permission in permissions)

    @staticmethod
    def filter_navigation(context: CompanyPlatformContext, navigation: Tuple[NavigationContract, ...]) -> Tuple[NavigationContract, ...]:
        context.require_access()
        resolved = []
        for item in navigation:
            if not item.enabled:
                continue
            if item.permission is not None and not context.has_permission(item.permission):
                continue
            if item.entitlement is not None and not context.has_entitlement(item.entitlement):
                continue
            resolved.append(item)
        return tuple(sorted(resolved, key=lambda item: (item.order, item.key)))
