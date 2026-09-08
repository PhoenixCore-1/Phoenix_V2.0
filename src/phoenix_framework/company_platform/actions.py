"""Controlled Company Platform administration action boundary."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyAdministrationAction(str, Enum):
    """Stable action identifiers for Company Platform administration."""

    USER_ADMINISTRATION = "company.users"
    ROLE_PERMISSION_ADMINISTRATION = "company.roles_permissions"
    DATA_VISIBILITY_ADMINISTRATION = "company.data_visibility"
    WORKSPACE_ADMINISTRATION = "company.workspaces"


class CompanyUserAction(str, Enum):
    """Supported Company Platform user-administration operations."""

    INVITE = "invite"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    ASSIGN_ROLE = "assign_role"
    REMOVE_ROLE = "remove_role"


@dataclass(frozen=True)
class CompanyUserAdministrationRequest:
    """Immutable tenant-bound user operation for an authoritative executor."""

    action: CompanyUserAction
    organisation_id: UUID
    identity_id: UUID | None
    role_id: UUID | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyUserAction,
        identity_id: UUID | None = None,
        role_id: UUID | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyUserAdministrationRequest":
        context.require_access()
        return cls(context.organisation_id, context.organisation_id, identity_id, role_id, tuple(sorted((parameters or {}).items())))

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("User administration request does not match request organisation")
        if self.action in {CompanyUserAction.ASSIGN_ROLE, CompanyUserAction.REMOVE_ROLE} and self.role_id is None:
            raise ValueError("Role operations require a role_id")


class CompanyUserAdministrationExecutor(Protocol):
    """Authoritative Core application boundary for user administration."""

    def execute(self, context: CompanyPlatformContext, request: CompanyUserAdministrationRequest) -> CompanyAdministrationResult: ...


@dataclass(frozen=True)
class CompanyAdministrationRequest:
    """Immutable tenant-bound request passed to an authoritative executor."""

    action: CompanyAdministrationAction
    organisation_id: UUID
    target_id: UUID | None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(cls, context: CompanyPlatformContext, *, action: CompanyAdministrationAction, target_id: UUID | None = None, parameters: Mapping[str, str] | None = None) -> "CompanyAdministrationRequest":
        context.require_access()
        return cls(action, context.organisation_id, target_id, tuple(sorted((parameters or {}).items())))

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Administration request does not match request organisation")


@dataclass(frozen=True)
class CompanyAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyAdministrationAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyAdministrationExecutor(Protocol):
    """Contract implemented by the authoritative Core application boundary."""

    def execute(self, context: CompanyPlatformContext, request: CompanyAdministrationRequest) -> CompanyAdministrationResult: ...


class CompanyAdministrationService:
    """Framework orchestration facade; never mutates Company Platform state."""

    @staticmethod
    def build_request(context: CompanyPlatformContext, *, action: CompanyAdministrationAction, target_id: UUID | None = None, parameters: Mapping[str, str] | None = None) -> CompanyAdministrationRequest:
        return CompanyAdministrationRequest.create(context, action=action, target_id=target_id, parameters=parameters)

    @staticmethod
    def execute(context: CompanyPlatformContext, request: CompanyAdministrationRequest, executor: CompanyAdministrationExecutor) -> CompanyAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)


class CompanyUserAdministrationService:
    """Framework facade for controlled user operations."""

    @staticmethod
    def build_request(context: CompanyPlatformContext, *, action: CompanyUserAction, identity_id: UUID | None = None, role_id: UUID | None = None, parameters: Mapping[str, str] | None = None) -> CompanyUserAdministrationRequest:
        return CompanyUserAdministrationRequest.create(context, action=action, identity_id=identity_id, role_id=role_id, parameters=parameters)

    @staticmethod
    def execute(context: CompanyPlatformContext, request: CompanyUserAdministrationRequest, executor: CompanyUserAdministrationExecutor) -> CompanyAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
