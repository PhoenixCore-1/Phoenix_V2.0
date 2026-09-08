"""Company Platform navigation and workspace resolution boundary."""

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.contracts import COMPANY_PLATFORM_NAVIGATION
from phoenix_framework.company_platform.workspaces import WorkspaceView
from phoenix_framework.contracts.navigation import NavigationContract


@dataclass(frozen=True)
class CompanyNavigationView:
    """Resolved navigation presented to the current tenant user."""

    organisation_id: UUID
    items: Tuple[NavigationContract, ...]
    workspace_id: UUID | None = None


class CompanyNavigationService:
    """Resolve presentation metadata without becoming an authorization engine."""

    @staticmethod
    def resolve_navigation(context: CompanyPlatformContext, *, navigation: Tuple[NavigationContract, ...] = COMPANY_PLATFORM_NAVIGATION, workspace: WorkspaceView | None = None) -> CompanyNavigationView:
        context.require_access()
        if workspace is not None and workspace.organisation_id != context.organisation_id:
            raise PermissionError("Workspace does not match request organisation")
        allowed_keys = None if workspace is None else set(workspace.navigation_keys)
        resolved = []
        for item in navigation:
            if not item.enabled:
                continue
            if allowed_keys is not None and item.key not in allowed_keys:
                continue
            if item.permission is not None and not context.has_permission(item.permission):
                continue
            if item.entitlement is not None and not context.has_entitlement(item.entitlement):
                continue
            resolved.append(item)
        resolved.sort(key=lambda item: (item.order, item.key))
        return CompanyNavigationView(context.organisation_id, tuple(resolved), None if workspace is None else workspace.workspace_id)

    @staticmethod
    def resolve_workspace(context: CompanyPlatformContext, workspaces: Tuple[WorkspaceView, ...]) -> WorkspaceView | None:
        context.require_access()
        tenant_workspaces = tuple(workspace for workspace in workspaces if workspace.organisation_id == context.organisation_id)
        if not tenant_workspaces:
            return None
        for workspace in tenant_workspaces:
            if workspace.default_workspace:
                return workspace
        return tenant_workspaces[0]
