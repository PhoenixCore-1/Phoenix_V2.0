"""Controlled Company Platform activity and audit administration boundary.

This layer defines tenant-bound presentation filters and export requests. It
never stores activity/audit records, changes retention policy, or bypasses
Core audit authority.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyActivityAuditAction(str, Enum):
    """Supported activity/audit administration operations."""

    SEARCH_ACTIVITY = "search_activity"
    SEARCH_AUDIT = "search_audit"
    REQUEST_ACTIVITY_EXPORT = "request_activity_export"
    REQUEST_AUDIT_EXPORT = "request_audit_export"
    VIEW_RETENTION_POLICY = "view_retention_policy"


@dataclass(frozen=True)
class CompanyActivityAuditAdministrationRequest:
    """Immutable tenant-bound activity/audit query or export request."""

    action: CompanyActivityAuditAction
    organisation_id: UUID
    filters: tuple[tuple[str, str], ...] = ()
    export_format: str | None = None

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyActivityAuditAction,
        filters: Mapping[str, str] | None = None,
        export_format: str | None = None,
    ) -> "CompanyActivityAuditAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            filters=tuple(sorted((filters or {}).items())),
            export_format=export_format,
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Activity/audit request does not match request organisation")
        export_actions = {
            CompanyActivityAuditAction.REQUEST_ACTIVITY_EXPORT,
            CompanyActivityAuditAction.REQUEST_AUDIT_EXPORT,
        }
        if self.action in export_actions and not self.export_format:
            raise ValueError("Export requests require an export_format")
        if self.action not in export_actions and self.export_format is not None:
            raise ValueError("export_format is only valid for export requests")


@dataclass(frozen=True)
class CompanyActivityAuditAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyActivityAuditAction
    organisation_id: UUID
    target_id: UUID | None
    success: bool
    message: str = ""


class CompanyActivityAuditAdministrationExecutor(Protocol):
    """Authoritative Core/application boundary for activity and audit access."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyActivityAuditAdministrationRequest,
    ) -> CompanyActivityAuditAdministrationResult: ...


class CompanyActivityAuditAdministrationService:
    """Framework facade; validates and delegates activity/audit operations."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyActivityAuditAction,
        filters: Mapping[str, str] | None = None,
        export_format: str | None = None,
    ) -> CompanyActivityAuditAdministrationRequest:
        return CompanyActivityAuditAdministrationRequest.create(
            context,
            action=action,
            filters=filters,
            export_format=export_format,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyActivityAuditAdministrationRequest,
        executor: CompanyActivityAuditAdministrationExecutor,
    ) -> CompanyActivityAuditAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
