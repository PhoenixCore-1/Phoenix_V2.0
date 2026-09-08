"""Company Platform workspace administration boundary.

Workspace configuration is presentation/orchestration metadata. Core remains
authoritative for identity, tenant context, authorization and entitlements;
this layer does not persist or enforce those concerns.
"""

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class WorkspaceView:
    """Read-only workspace configuration for a tenant user."""

    workspace_id: UUID
    name: str
    navigation_keys: Tuple[str, ...]
    dashboard_keys: Tuple[str, ...]
    default_workspace: bool
    organisation_id: UUID

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        workspace_id: UUID,
        name: str,
        navigation_keys: Tuple[str, ...],
        dashboard_keys: Tuple[str, ...],
        default_workspace: bool,
        organisation_id: UUID,
    ) -> "WorkspaceView":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Workspace does not match request organisation")
        return cls(
            workspace_id=workspace_id,
            name=name,
            navigation_keys=tuple(navigation_keys),
            dashboard_keys=tuple(dashboard_keys),
            default_workspace=default_workspace,
            organisation_id=organisation_id,
        )


@dataclass(frozen=True)
class CompanyWorkspacesView:
    """Read-only tenant workspace collection."""

    organisation_id: UUID
    workspaces: Tuple[WorkspaceView, ...]


class CompanyWorkspaceAdministrationService:
    """Framework orchestration boundary for workspace administration."""

    @staticmethod
    def get_workspace_view(context: CompanyPlatformContext, **workspace: object) -> WorkspaceView:
        return WorkspaceView.from_core(context, **workspace)

    @staticmethod
    def get_workspaces_view(
        context: CompanyPlatformContext,
        workspaces: Tuple[WorkspaceView, ...],
    ) -> CompanyWorkspacesView:
        context.require_access()
        for workspace in workspaces:
            if workspace.organisation_id != context.organisation_id:
                raise PermissionError("Workspace does not match request organisation")
        return CompanyWorkspacesView(context.organisation_id, tuple(workspaces))
