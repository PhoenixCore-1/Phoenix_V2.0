"""Controlled Company Platform reporting administration boundary.

The Framework creates immutable tenant-bound report administration requests
and delegates execution/configuration to authoritative Core or domain report
services. It does not persist report data or implement report authorization.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyReportingAction(str, Enum):
    """Supported Company Platform reporting operations."""

    CREATE_REPORT_DEFINITION = "create_report_definition"
    UPDATE_REPORT_DEFINITION = "update_report_definition"
    ENABLE_REPORT = "enable_report"
    DISABLE_REPORT = "disable_report"
    EXECUTE_REPORT = "execute_report"
    SCHEDULE_REPORT = "schedule_report"
    CANCEL_REPORT_SCHEDULE = "cancel_report_schedule"
    EXPORT_REPORT = "export_report"


@dataclass(frozen=True)
class CompanyReportingAdministrationRequest:
    """Immutable tenant-bound reporting operation."""

    action: CompanyReportingAction
    organisation_id: UUID
    report_id: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyReportingAction,
        report_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyReportingAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            report_id=report_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Reporting administration request does not match request organisation")

        existing_report_actions = {
            CompanyReportingAction.UPDATE_REPORT_DEFINITION,
            CompanyReportingAction.ENABLE_REPORT,
            CompanyReportingAction.DISABLE_REPORT,
            CompanyReportingAction.EXECUTE_REPORT,
            CompanyReportingAction.SCHEDULE_REPORT,
            CompanyReportingAction.CANCEL_REPORT_SCHEDULE,
            CompanyReportingAction.EXPORT_REPORT,
        }
        if self.action in existing_report_actions and not self.report_id:
            raise ValueError("This reporting operation requires a report_id")

        if self.action == CompanyReportingAction.CREATE_REPORT_DEFINITION and not self.parameters:
            raise ValueError("Report definition creation requires report parameters")

        if self.action == CompanyReportingAction.UPDATE_REPORT_DEFINITION and not self.parameters:
            raise ValueError("Report definition update requires report parameters")

        if self.action == CompanyReportingAction.SCHEDULE_REPORT:
            parameter_names = {key for key, _ in self.parameters}
            if "schedule" not in parameter_names:
                raise ValueError("Report scheduling requires a schedule parameter")

        if self.action == CompanyReportingAction.EXPORT_REPORT:
            parameter_names = {key for key, _ in self.parameters}
            if "format" not in parameter_names:
                raise ValueError("Report export requires a format parameter")


@dataclass(frozen=True)
class CompanyReportingAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyReportingAction
    organisation_id: UUID
    target_id: str | None
    success: bool
    message: str = ""


class CompanyReportingAdministrationExecutor(Protocol):
    """Authoritative Core/domain application boundary for report operations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyReportingAdministrationRequest,
    ) -> CompanyReportingAdministrationResult: ...


class CompanyReportingAdministrationService:
    """Framework facade; validates and delegates report administration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyReportingAction,
        report_id: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyReportingAdministrationRequest:
        return CompanyReportingAdministrationRequest.create(
            context,
            action=action,
            report_id=report_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyReportingAdministrationRequest,
        executor: CompanyReportingAdministrationExecutor,
    ) -> CompanyReportingAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
