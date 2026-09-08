"""Company Platform request context boundary."""

from dataclasses import dataclass

from phoenix_framework.context import FrameworkContext


@dataclass(frozen=True)
class CompanyPlatformContext:
    """Validated tenant-scoped context for Company Platform consumers."""

    framework: FrameworkContext

    def require_access(self) -> None:
        """Require an authenticated identity and tenant-bound request."""
        self.framework.require_authenticated()
        self.framework.require_tenant()

    @property
    def organisation_id(self):
        return self.framework.organisation_id

    def has_permission(self, permission: str) -> bool:
        return self.framework.has_permission(permission)

    def has_entitlement(self, entitlement: str) -> bool:
        return self.framework.has_entitlement(entitlement)
