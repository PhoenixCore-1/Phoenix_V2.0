"""Company Platform user administration projection boundary.

Identity, membership, authentication and authorization remain authoritative in
Phoenix Core. This Framework surface only projects Core-supplied user data for
presentation and orchestration within the current tenant.
"""

from dataclasses import dataclass
from typing import FrozenSet, Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.contracts import UserContext


@dataclass(frozen=True)
class CompanyUserView:
    """Read-only tenant-scoped user administration view."""

    identity_id: UUID
    username: str
    display_name: str
    organisation_id: UUID
    permissions: FrozenSet[str]
    entitlements: FrozenSet[str]

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        user: UserContext,
    ) -> "CompanyUserView":
        """Project an authoritative Core user context into Company Platform."""
        context.require_access()
        if user.organisation_id != context.organisation_id:
            raise PermissionError("User context does not match request organisation")
        return cls(
            identity_id=user.identity_id,
            username=user.username,
            display_name=user.display_name,
            organisation_id=user.organisation_id,
            permissions=frozenset(user.permissions),
            entitlements=frozenset(user.entitlements),
        )


@dataclass(frozen=True)
class CompanyUsersView:
    """Read-only collection of users belonging to the current tenant."""

    organisation_id: UUID
    users: Tuple[CompanyUserView, ...]

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        users: Tuple[UserContext, ...],
    ) -> "CompanyUsersView":
        context.require_access()
        projected = tuple(CompanyUserView.from_core(context, user) for user in users)
        return cls(organisation_id=context.organisation_id, users=projected)


class CompanyUserAdministrationService:
    """Framework orchestration boundary for tenant user administration."""

    @staticmethod
    def get_user_view(
        context: CompanyPlatformContext,
        user: UserContext,
    ) -> CompanyUserView:
        return CompanyUserView.from_core(context, user)

    @staticmethod
    def get_users_view(
        context: CompanyPlatformContext,
        users: Tuple[UserContext, ...],
    ) -> CompanyUsersView:
        return CompanyUsersView.from_core(context, users)
