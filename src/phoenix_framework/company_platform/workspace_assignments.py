"""Controlled Company Platform user-workspace assignment boundary.

The Framework builds immutable tenant-bound assignment requests and delegates
all assignment mutations to an authoritative application executor. Identity,
membership, authorization and persistence remain outside this layer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyWorkspaceAssignmentAction(str, Enum):
    """Supported user-workspace assignment operations."""

    ASSIGN_WORKSPACE = "assign_workspace"
    REMOVE_WORKSPACE = "remove_workspace"
    SET_DEFAULT_WORKSPACE = "set_default_workspace"
    CLEAR_DEFAULT_WORKSPACE = "clear_default_workspace"


@dataclass(frozen=True)
class CompanyWorkspaceAssignmentRequest:
    """Immutable tenant-bound user-workspace assignment operation."""

    action: CompanyWorkspaceAssignmentAction
    organisation_id: UUID
    identity_id: UUID
    workspace_id: UUID
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkspaceAssignmentAction,
        identity_id: UUID,
        workspace_id: UUID,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyWorkspaceAssignmentRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=identity_id,
            workspace_id=workspace_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Workspace assignment request does not match request organisation")
        if not self.identity_id:
            raise ValueError("Workspace assignment requires an identity_id")
        if not self.workspace_id:
            raise ValueError("Workspace assignment requires a workspace_id")


@dataclass(frozen=True)
class CompanyWorkspaceAssignmentResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyWorkspaceAssignmentAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyWorkspaceAssignmentExecutor(Protocol):
    """Authoritative Core/application boundary for workspace assignments."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyWorkspaceAssignmentRequest,
    ) -> CompanyWorkspaceAssignmentResult: ...


class CompanyWorkspaceAssignmentService:
    """Framework facade; validates and delegates assignment mutations only."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkspaceAssignmentAction,
        identity_id: UUID,
        workspace_id: UUID,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyWorkspaceAssignmentRequest:
        return CompanyWorkspaceAssignmentRequest.create(
            context,
            action=action,
            identity_id=identity_id,
            workspace_id=workspace_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyWorkspaceAssignmentRequest,
        executor: CompanyWorkspaceAssignmentExecutor,
    ) -> CompanyWorkspaceAssignmentResult:
        request.validate_for(context)
        return executor.execute(context, request)
