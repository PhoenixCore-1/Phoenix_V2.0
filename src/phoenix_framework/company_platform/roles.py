"""Company Platform roles and permissions administration boundary.

Authorization authority remains in Phoenix Core. This Framework surface only
projects Core-supplied role and permission definitions for tenant administration
and does not persist or enforce authorization rules itself.
"""

from dataclasses import dataclass
from typing import FrozenSet, Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class CompanyRoleView:
    """Read-only tenant role projection."""

    role_id: UUID
    name: str
    description: str
    permissions: FrozenSet[str]
    organisation_id: UUID

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        role_id: UUID,
        name: str,
        description: str,
        permissions: FrozenSet[str],
        organisation_id: UUID,
    ) -> "CompanyRoleView":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Role does not match request organisation")
        return cls(
            role_id=role_id,
            name=name,
            description=description,
            permissions=frozenset(permissions),
            organisation_id=organisation_id,
        )


@dataclass(frozen=True)
class CompanyPermissionView:
    """Read-only permission projection."""

    code: str
    name: str
    description: str


@dataclass(frozen=True)
class CompanyRolesPermissionsView:
    """Read-only tenant-scoped roles and permissions collection."""

    organisation_id: UUID
    roles: Tuple[CompanyRoleView, ...]
    permissions: Tuple[CompanyPermissionView, ...]


class CompanyRolesPermissionsService:
    """Framework orchestration boundary for roles and permissions administration."""

    @staticmethod
    def get_role_view(
        context: CompanyPlatformContext,
        *,
        role_id: UUID,
        name: str,
        description: str,
        permissions: FrozenSet[str],
        organisation_id: UUID,
    ) -> CompanyRoleView:
        return CompanyRoleView.from_core(
            context,
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions,
            organisation_id=organisation_id,
        )

    @staticmethod
    def get_roles_permissions_view(
        context: CompanyPlatformContext,
        *,
        roles: Tuple[CompanyRoleView, ...],
        permissions: Tuple[CompanyPermissionView, ...],
    ) -> CompanyRolesPermissionsView:
        context.require_access()
        for role in roles:
            if role.organisation_id != context.organisation_id:
                raise PermissionError("Role does not match request organisation")
        return CompanyRolesPermissionsView(
            organisation_id=context.organisation_id,
            roles=tuple(roles),
            permissions=tuple(permissions),
        )
