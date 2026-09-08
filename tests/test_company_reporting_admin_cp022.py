from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.reporting_admin import (
    CompanyReportingAction,
    CompanyReportingAdministrationRequest,
    CompanyReportingAdministrationResult,
    CompanyReportingAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyReportingAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=request.report_id,
            success=True,
            message="delegated",
        )


def make_context():
    return CompanyPlatformContext.from_core(
        RequestContext(
            request_id=str(uuid4()),
            identity_id=uuid4(),
            organisation_id=uuid4(),
        )
    )


def test_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyReportingAdministrationService.build_request(
        context,
        action=CompanyReportingAction.CREATE_REPORT_DEFINITION,
        parameters={"name": "Sales Summary"},
    )
    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("name", "Sales Summary"),)
    with pytest.raises(FrozenInstanceError):
        request.report_id = "changed"


def test_existing_report_operations_require_report_id():
    context = make_context()
    for action in (
        CompanyReportingAction.UPDATE_REPORT_DEFINITION,
        CompanyReportingAction.ENABLE_REPORT,
        CompanyReportingAction.DISABLE_REPORT,
        CompanyReportingAction.EXECUTE_REPORT,
        CompanyReportingAction.SCHEDULE_REPORT,
        CompanyReportingAction.CANCEL_REPORT_SCHEDULE,
        CompanyReportingAction.EXPORT_REPORT,
    ):
        request = CompanyReportingAdministrationRequest.create(
            context,
            action=action,
            parameters={"schedule": "daily"} if action == CompanyReportingAction.SCHEDULE_REPORT else ({"format": "csv"} if action == CompanyReportingAction.EXPORT_REPORT else ({"name": "Updated"} if action == CompanyReportingAction.UPDATE_REPORT_DEFINITION else None)),
        )
        with pytest.raises(ValueError, match="report_id"):
            request.validate_for(context)


def test_create_and_update_require_definition_parameters():
    context = make_context()
    for action, report_id in (
        (CompanyReportingAction.CREATE_REPORT_DEFINITION, None),
        (CompanyReportingAction.UPDATE_REPORT_DEFINITION, "sales"),
    ):
        request = CompanyReportingAdministrationRequest.create(
            context, action=action, report_id=report_id
        )
        with pytest.raises(ValueError, match="report parameters"):
            request.validate_for(context)


def test_schedule_and_export_require_specific_parameters():
    context = make_context()
    schedule_request = CompanyReportingAdministrationRequest.create(
        context, action=CompanyReportingAction.SCHEDULE_REPORT, report_id="sales"
    )
    with pytest.raises(ValueError, match="schedule parameter"):
        schedule_request.validate_for(context)

    export_request = CompanyReportingAdministrationRequest.create(
        context, action=CompanyReportingAction.EXPORT_REPORT, report_id="sales"
    )
    with pytest.raises(ValueError, match="format parameter"):
        export_request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyReportingAdministrationRequest(
        action=CompanyReportingAction.EXECUTE_REPORT,
        organisation_id=uuid4(),
        report_id="sales",
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyReportingAdministrationService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyReportingAdministrationService.build_request(
        context,
        action=CompanyReportingAction.EXPORT_REPORT,
        report_id="sales",
        parameters={"format": "csv"},
    )
    result = CompanyReportingAdministrationService.execute(context, request, executor)
    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyReportingAdministrationService.build_request(
            context,
            action=CompanyReportingAction.EXECUTE_REPORT,
            report_id="sales",
        )
