"""Controlled Company Platform user-level data-visibility boundary.

User-specific visibility is represented as an immutable tenant-bound request
and delegated to an authoritative application executor. This layer does not
implement authorization semantics or persist visibility assignments.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyUserVisibilityAction(str, Enum):
    """Supported user-level visibility operations."""

    GRANT_USER_SCOPE = "grant_user_scope"
    REVOKE_USER_SCOPE = "revoke_user_scope"
    SET_USER_VISIBILITY = "set_user_visibility"
    CLEAR_USER_VISIBILITY = "clear_user_visibility"


@dataclass(frozen=True)
class CompanyUserVisibilityAdministrationRequest:
    """Immutable tenant-bound user visibility operation."""

    action: CompanyUserVisibilityAction
    organisation_id: UUID
    identity_id: UUID
    resource: str
    scope: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyUserVisibilityAction,
        identity_id: UUID,
        resource: str,
        scope: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyUserVisibilityAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=identity_id,
            resource=resource,
            scope=scope,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("User visibility request does not match request organisation")
        if not self.identity_id:
            raise ValueError("User visibility administration requires an identity_id")
        if not self.resource:
            raise ValueError("User visibility administration requires a resource")
        if self.action in {
            CompanyUserVisibilityAction.GRANT_USER_SCOPE,
            CompanyUserVisibilityAction.SET_USER_VISIBILITY,
        } and not self.scope:
            raise ValueError("This user visibility operation requires a scope")


@dataclass(frozen=True)
class CompanyUserVisibilityAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyUserVisibilityAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyUserVisibilityAdministrationExecutor(Protocol):
    """Authoritative Core/application boundary for user visibility mutations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyUserVisibilityAdministrationRequest,
    ) -> CompanyUserVisibilityAdministrationResult: ...


class CompanyUserVisibilityAdministrationService:
    """Framework facade; validates and delegates user visibility mutations."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyUserVisibilityAction,
        identity_id: UUID,
        resource: str,
        scope: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyUserVisibilityAdministrationRequest:
        return CompanyUserVisibilityAdministrationRequest.create(
            context,
            action=action,
            identity_id=identity_id,
            resource=resource,
            scope=scope,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyUserVisibilityAdministrationRequest,
        executor: CompanyUserVisibilityAdministrationExecutor,
    ) -> CompanyUserVisibilityAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
