"""Controlled Company Platform module experience administration boundary."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyModuleExperienceAction(str, Enum):
    """Supported tenant-level module presentation operations."""

    SET_MODULE_VISIBILITY = "set_module_visibility"
    UPDATE_MODULE_NAVIGATION = "update_module_navigation"
    ENABLE_MODULE_IN_WORKSPACE = "enable_module_in_workspace"
    DISABLE_MODULE_IN_WORKSPACE = "disable_module_in_workspace"
    UPDATE_MODULE_PRESENTATION = "update_module_presentation"
    SET_MODULE_DEFAULT_VIEW = "set_module_default_view"


@dataclass(frozen=True)
class CompanyModuleExperienceAdministrationRequest:
    """Immutable tenant-bound module experience operation."""

    action: CompanyModuleExperienceAction
    organisation_id: UUID
    module_code: str
    workspace_id: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyModuleExperienceAction,
        module_code: str,
        workspace_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyModuleExperienceAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            module_code=module_code,
            workspace_id=workspace_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Module experience request does not match request organisation")
        if not self.module_code.strip():
            raise ValueError("Module experience operation requires a module code")

        workspace_actions = {
            CompanyModuleExperienceAction.ENABLE_MODULE_IN_WORKSPACE,
            CompanyModuleExperienceAction.DISABLE_MODULE_IN_WORKSPACE,
        }
        if self.action in workspace_actions and not self.workspace_id:
            raise ValueError("This module experience operation requires a workspace_id")

        parameter_actions = {
            CompanyModuleExperienceAction.UPDATE_MODULE_NAVIGATION,
            CompanyModuleExperienceAction.UPDATE_MODULE_PRESENTATION,
        }
        if self.action in parameter_actions and not self.parameters:
            raise ValueError("This module experience operation requires parameters")

        if self.action == CompanyModuleExperienceAction.SET_MODULE_DEFAULT_VIEW and not self.parameters:
            raise ValueError("Setting the module default view requires parameters")


@dataclass(frozen=True)
class CompanyModuleExperienceAdministrationResult:
    """Immutable result returned by the authoritative module experience executor."""

    action: CompanyModuleExperienceAction
    organisation_id: UUID
    module_code: str
    workspace_id: str | None
    success: bool
    message: str = ""


class CompanyModuleExperienceAdministrationExecutor(Protocol):
    """Authoritative application boundary for module experience operations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyModuleExperienceAdministrationRequest,
    ) -> CompanyModuleExperienceAdministrationResult: ...


class CompanyModuleExperienceAdministrationService:
    """Framework facade; validates and delegates module experience administration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyModuleExperienceAction,
        module_code: str,
        workspace_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyModuleExperienceAdministrationRequest:
        return CompanyModuleExperienceAdministrationRequest.create(
            context,
            action=action,
            module_code=module_code,
            workspace_id=workspace_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyModuleExperienceAdministrationRequest,
        executor: CompanyModuleExperienceAdministrationExecutor,
    ) -> CompanyModuleExperienceAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
