"""Controlled Company Platform workspace administration boundary.

The Framework builds immutable tenant-bound workspace requests and delegates
all workspace mutations to an authoritative application executor. Workspace
metadata remains presentation/orchestration data; Core remains authoritative
for security, tenancy, authorization and entitlements.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyWorkspaceAction(str, Enum):
    """Supported Company Platform workspace operations."""

    CREATE_WORKSPACE = "create_workspace"
    UPDATE_WORKSPACE = "update_workspace"
    ACTIVATE_WORKSPACE = "activate_workspace"
    DEACTIVATE_WORKSPACE = "deactivate_workspace"
    SET_DEFAULT_WORKSPACE = "set_default_workspace"
    UPDATE_NAVIGATION = "update_navigation"
    UPDATE_DASHBOARD = "update_dashboard"


@dataclass(frozen=True)
class CompanyWorkspaceAdministrationRequest:
    """Immutable tenant-bound workspace operation."""

    action: CompanyWorkspaceAction
    organisation_id: UUID
    workspace_id: UUID | None = None
    navigation_keys: tuple[str, ...] = ()
    dashboard_keys: tuple[str, ...] = ()
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkspaceAction,
        workspace_id: UUID | None = None,
        navigation_keys: tuple[str, ...] | None = None,
        dashboard_keys: tuple[str, ...] | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyWorkspaceAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            workspace_id=workspace_id,
            navigation_keys=tuple(navigation_keys or ()),
            dashboard_keys=tuple(dashboard_keys or ()),
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Workspace administration request does not match request organisation")

        existing_workspace_actions = {
            CompanyWorkspaceAction.UPDATE_WORKSPACE,
            CompanyWorkspaceAction.ACTIVATE_WORKSPACE,
            CompanyWorkspaceAction.DEACTIVATE_WORKSPACE,
            CompanyWorkspaceAction.SET_DEFAULT_WORKSPACE,
            CompanyWorkspaceAction.UPDATE_NAVIGATION,
            CompanyWorkspaceAction.UPDATE_DASHBOARD,
        }
        if self.action in existing_workspace_actions and self.workspace_id is None:
            raise ValueError("This workspace operation requires a workspace_id")

        if self.action in {
            CompanyWorkspaceAction.CREATE_WORKSPACE,
            CompanyWorkspaceAction.UPDATE_WORKSPACE,
        } and not self.parameters:
            raise ValueError("Workspace creation or update requires workspace parameters")

        if self.action == CompanyWorkspaceAction.UPDATE_NAVIGATION and not self.navigation_keys:
            raise ValueError("Navigation updates require navigation_keys")

        if self.action == CompanyWorkspaceAction.UPDATE_DASHBOARD and not self.dashboard_keys:
            raise ValueError("Dashboard updates require dashboard_keys")


class CompanyWorkspaceAdministrationExecutor(Protocol):
    """Authoritative Core/application boundary for workspace mutations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyWorkspaceAdministrationRequest,
    ) -> "CompanyWorkspaceAdministrationResult": ...


@dataclass(frozen=True)
class CompanyWorkspaceAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyWorkspaceAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyWorkspaceAdministrationOperationService:
    """Framework facade; validates and delegates workspace mutations only."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkspaceAction,
        workspace_id: UUID | None = None,
        navigation_keys: tuple[str, ...] | None = None,
        dashboard_keys: tuple[str, ...] | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyWorkspaceAdministrationRequest:
        return CompanyWorkspaceAdministrationRequest.create(
            context,
            action=action,
            workspace_id=workspace_id,
            navigation_keys=navigation_keys,
            dashboard_keys=dashboard_keys,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyWorkspaceAdministrationRequest,
        executor: CompanyWorkspaceAdministrationExecutor,
    ) -> CompanyWorkspaceAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
