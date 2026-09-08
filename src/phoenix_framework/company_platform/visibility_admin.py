"""Controlled Company Platform data-visibility administration boundary.

The Framework defines immutable tenant-bound requests and delegates all
visibility-rule mutations to an authoritative Core/application executor.
It does not implement authorization semantics or persistence.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyVisibilityAction(str, Enum):
    """Supported Company Platform data-visibility operations."""

    CREATE_RULE = "create_rule"
    UPDATE_RULE = "update_rule"
    ENABLE_RULE = "enable_rule"
    DISABLE_RULE = "disable_rule"
    ADD_ROLE_SCOPE = "add_role_scope"
    REMOVE_ROLE_SCOPE = "remove_role_scope"
    UPDATE_RESOURCE_SCOPE = "update_resource_scope"


@dataclass(frozen=True)
class CompanyVisibilityAdministrationRequest:
    """Immutable tenant-bound visibility operation for an authoritative executor."""

    action: CompanyVisibilityAction
    organisation_id: UUID
    rule_id: UUID | None = None
    role_scope: str | None = None
    resource_scope: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyVisibilityAction,
        rule_id: UUID | None = None,
        role_scope: str | None = None,
        resource_scope: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyVisibilityAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            rule_id=rule_id,
            role_scope=role_scope,
            resource_scope=resource_scope,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Visibility administration request does not match request organisation")

        existing_rule_actions = {
            CompanyVisibilityAction.UPDATE_RULE,
            CompanyVisibilityAction.ENABLE_RULE,
            CompanyVisibilityAction.DISABLE_RULE,
            CompanyVisibilityAction.ADD_ROLE_SCOPE,
            CompanyVisibilityAction.REMOVE_ROLE_SCOPE,
            CompanyVisibilityAction.UPDATE_RESOURCE_SCOPE,
        }
        if self.action in existing_rule_actions and self.rule_id is None:
            raise ValueError("This visibility operation requires a rule_id")

        if self.action in {
            CompanyVisibilityAction.ADD_ROLE_SCOPE,
            CompanyVisibilityAction.REMOVE_ROLE_SCOPE,
        } and not self.role_scope:
            raise ValueError("Role scope operations require a role_scope")

        if self.action in {
            CompanyVisibilityAction.CREATE_RULE,
            CompanyVisibilityAction.UPDATE_RULE,
            CompanyVisibilityAction.UPDATE_RESOURCE_SCOPE,
        } and not self.resource_scope:
            raise ValueError("This visibility operation requires a resource_scope")


class CompanyVisibilityAdministrationExecutor(Protocol):
    """Authoritative Core/application boundary for visibility mutations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyVisibilityAdministrationRequest,
    ) -> "CompanyVisibilityAdministrationResult": ...


@dataclass(frozen=True)
class CompanyVisibilityAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyVisibilityAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyVisibilityAdministrationService:
    """Framework facade; validation only, with mutation delegated to Core."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyVisibilityAction,
        rule_id: UUID | None = None,
        role_scope: str | None = None,
        resource_scope: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyVisibilityAdministrationRequest:
        return CompanyVisibilityAdministrationRequest.create(
            context,
            action=action,
            rule_id=rule_id,
            role_scope=role_scope,
            resource_scope=resource_scope,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyVisibilityAdministrationRequest,
        executor: CompanyVisibilityAdministrationExecutor,
    ) -> CompanyVisibilityAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
