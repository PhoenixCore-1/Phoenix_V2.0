"""Controlled Company Platform workflow administration boundary."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyWorkflowAction(str, Enum):
    """Supported tenant-level workflow administration operations."""

    ENABLE_WORKFLOW = "enable_workflow"
    DISABLE_WORKFLOW = "disable_workflow"
    UPDATE_WORKFLOW_CONFIGURATION = "update_workflow_configuration"
    ASSIGN_WORKFLOW = "assign_workflow"
    UNASSIGN_WORKFLOW = "unassign_workflow"
    START_WORKFLOW = "start_workflow"
    PAUSE_WORKFLOW = "pause_workflow"
    RESUME_WORKFLOW = "resume_workflow"
    CANCEL_WORKFLOW = "cancel_workflow"


@dataclass(frozen=True)
class CompanyWorkflowAdministrationRequest:
    """Immutable tenant-bound workflow operation."""

    action: CompanyWorkflowAction
    organisation_id: UUID
    workflow_key: str
    target_id: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkflowAction,
        workflow_key: str,
        target_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyWorkflowAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            workflow_key=workflow_key,
            target_id=target_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Workflow request does not match request organisation")
        if not self.workflow_key.strip():
            raise ValueError("Workflow operation requires a workflow key")

        target_actions = {
            CompanyWorkflowAction.ASSIGN_WORKFLOW,
            CompanyWorkflowAction.UNASSIGN_WORKFLOW,
            CompanyWorkflowAction.START_WORKFLOW,
            CompanyWorkflowAction.PAUSE_WORKFLOW,
            CompanyWorkflowAction.RESUME_WORKFLOW,
            CompanyWorkflowAction.CANCEL_WORKFLOW,
        }
        if self.action in target_actions and not self.target_id:
            raise ValueError("This workflow operation requires a target_id")

        if self.action == CompanyWorkflowAction.UPDATE_WORKFLOW_CONFIGURATION and not self.parameters:
            raise ValueError("Workflow configuration update requires parameters")


@dataclass(frozen=True)
class CompanyWorkflowAdministrationResult:
    """Immutable result returned by the authoritative workflow executor."""

    action: CompanyWorkflowAction
    organisation_id: UUID
    workflow_key: str
    target_id: str | None
    success: bool
    message: str = ""


class CompanyWorkflowAdministrationExecutor(Protocol):
    """Authoritative Core/domain application boundary for workflow operations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyWorkflowAdministrationRequest,
    ) -> CompanyWorkflowAdministrationResult: ...


class CompanyWorkflowAdministrationService:
    """Framework facade; validates and delegates workflow administration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyWorkflowAction,
        workflow_key: str,
        target_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyWorkflowAdministrationRequest:
        return CompanyWorkflowAdministrationRequest.create(
            context,
            action=action,
            workflow_key=workflow_key,
            target_id=target_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyWorkflowAdministrationRequest,
        executor: CompanyWorkflowAdministrationExecutor,
    ) -> CompanyWorkflowAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
