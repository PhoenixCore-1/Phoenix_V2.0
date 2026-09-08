"""Company Platform reporting presentation boundary.

Reports are tenant-scoped projections over authoritative Core or business-module
reporting services. The Framework does not persist report data or replace the
authorization, entitlement, or domain authority of the source system.
"""

from dataclasses import dataclass
from typing import Mapping, Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class CompanyReportDefinitionView:
    """Read-only metadata describing a company report."""

    report_id: str
    name: str
    description: str
    source: str
    organisation_id: UUID
    permitted: bool = True

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        report_id: str,
        name: str,
        description: str,
        source: str,
        organisation_id: UUID,
        permitted: bool = True,
    ) -> "CompanyReportDefinitionView":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Report does not match request organisation")
        return cls(report_id, name, description, source, organisation_id, permitted)


@dataclass(frozen=True)
class CompanyReportResultView:
    """Read-only report result supplied by an authoritative reporting source."""

    report_id: str
    generated_at: str
    columns: Tuple[str, ...]
    rows: Tuple[Tuple[object, ...], ...]
    organisation_id: UUID

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        report_id: str,
        generated_at: str,
        columns: Tuple[str, ...],
        rows: Tuple[Tuple[object, ...], ...],
        organisation_id: UUID,
    ) -> "CompanyReportResultView":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Report result does not match request organisation")
        return cls(report_id, generated_at, tuple(columns), tuple(tuple(row) for row in rows), organisation_id)


@dataclass(frozen=True)
class CompanyReportingView:
    """Read-only tenant reporting catalogue and optional results."""

    organisation_id: UUID
    reports: Tuple[CompanyReportDefinitionView, ...]


class CompanyReportingService:
    """Framework orchestration boundary for company reporting presentation."""

    @staticmethod
    def get_report_definition(context: CompanyPlatformContext, **report: object) -> CompanyReportDefinitionView:
        return CompanyReportDefinitionView.from_core(context, **report)

    @staticmethod
    def get_reporting_view(
        context: CompanyPlatformContext,
        reports: Tuple[CompanyReportDefinitionView, ...],
    ) -> CompanyReportingView:
        context.require_access()
        for report in reports:
            if report.organisation_id != context.organisation_id:
                raise PermissionError("Report does not match request organisation")
        return CompanyReportingView(context.organisation_id, tuple(reports))

    @staticmethod
    def get_report_result(context: CompanyPlatformContext, **result: object) -> CompanyReportResultView:
        return CompanyReportResultView.from_core(context, **result)
