"""Controlled Company Platform administration action boundary.

Company Platform does not own identity, membership, authorization, visibility,
or workspace persistence. This module defines immutable, tenant-bound action
requests that an authorised Core application service may execute.
"""

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


@dataclass(frozen=True)
class CompanyAdministrationRequest:
    """Immutable tenant-bound request passed to an authoritative executor."""

    action: CompanyAdministrationAction
    organisation_id: UUID
    target_id: UUID | None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyAdministrationAction,
        target_id: UUID | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            target_id=target_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        """Ensure an action cannot be replayed across tenant boundaries."""
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

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyAdministrationRequest,
    ) -> CompanyAdministrationResult: ...


class CompanyAdministrationService:
    """Framework orchestration facade; never mutates Company Platform state."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyAdministrationAction,
        target_id: UUID | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyAdministrationRequest:
        return CompanyAdministrationRequest.create(
            context,
            action=action,
            target_id=target_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyAdministrationRequest,
        executor: CompanyAdministrationExecutor,
    ) -> CompanyAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
