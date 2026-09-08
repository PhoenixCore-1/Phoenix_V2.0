from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.reporting import (
    CompanyReportDefinitionView,
    CompanyReportResultView,
    CompanyReportingService,
)


def make_context(*, organisation_id=None, identity_id=None):
    core = RequestContext(
        request_id=uuid4(),
        identity_id=identity_id if identity_id is not None else uuid4(),
        organisation_id=organisation_id if organisation_id is not None else uuid4(),
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    return CompanyPlatformContext.from_core(core)


def test_report_definition_projects_authoritative_tenant_metadata():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id)

    report = CompanyReportingService.get_report_definition(
        context,
        report_id="user-activity",
        name="User Activity",
        description="Company user activity summary",
        source="core.audit",
        organisation_id=organisation_id,
    )

    assert report.organisation_id == organisation_id
    assert report.report_id == "user-activity"
    assert report.source == "core.audit"


def test_cross_tenant_report_definition_is_rejected():
    context = make_context(organisation_id=uuid4())

    with pytest.raises(PermissionError):
        CompanyReportDefinitionView.from_core(
            context,
            report_id="users",
            name="Users",
            description="User summary",
            source="core.identity",
            organisation_id=uuid4(),
        )


def test_reporting_collection_rejects_cross_tenant_report():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id)
    report = CompanyReportDefinitionView(
        report_id="users",
        name="Users",
        description="User summary",
        source="core.identity",
        organisation_id=uuid4(),
    )

    with pytest.raises(PermissionError):
        CompanyReportingService.get_reporting_view(context, (report,))


def test_report_result_is_tenant_scoped_and_read_only():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id)

    result = CompanyReportingService.get_report_result(
        context,
        report_id="users",
        generated_at="2026-09-08T00:00:00Z",
        columns=("username", "status"),
        rows=(("alice", "active"),),
        organisation_id=organisation_id,
    )

    assert isinstance(result, CompanyReportResultView)
    assert result.rows == (("alice", "active"),)
    with pytest.raises(Exception):
        result.report_id = "other"  # frozen dataclass


def test_report_requires_authenticated_tenant_context():
    core = RequestContext(
        request_id=uuid4(),
        identity_id=None,
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    context = CompanyPlatformContext.from_core(core)

    with pytest.raises(PermissionError):
        CompanyReportingService.get_report_definition(
            context,
            report_id="users",
            name="Users",
            description="User summary",
            source="core.identity",
            organisation_id=core.organisation_id,
        )
