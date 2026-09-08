from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.activity_audit_admin import (
    CompanyActivityAuditAction,
    CompanyActivityAuditAdministrationRequest,
    CompanyActivityAuditAdministrationResult,
    CompanyActivityAuditAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyActivityAuditAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=None,
            success=True,
            message="delegated",
        )


def make_context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyActivityAuditAdministrationService.build_request(
        context,
        action=CompanyActivityAuditAction.SEARCH_AUDIT,
        filters={"resource": "account", "outcome": "success"},
    )
    assert request.organisation_id == context.organisation_id
    assert request.filters == (("outcome", "success"), ("resource", "account"))
    with pytest.raises(FrozenInstanceError):
        request.organisation_id = uuid4()


def test_export_requests_require_format():
    context = make_context()
    for action in (
        CompanyActivityAuditAction.REQUEST_ACTIVITY_EXPORT,
        CompanyActivityAuditAction.REQUEST_AUDIT_EXPORT,
    ):
        request = CompanyActivityAuditAdministrationRequest.create(context, action=action)
        with pytest.raises(ValueError, match="export_format"):
            request.validate_for(context)


def test_non_export_requests_reject_export_format():
    context = make_context()
    request = CompanyActivityAuditAdministrationRequest.create(
        context,
        action=CompanyActivityAuditAction.SEARCH_ACTIVITY,
        export_format="csv",
    )
    with pytest.raises(ValueError, match="only valid for export requests"):
        request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyActivityAuditAdministrationRequest(
        action=CompanyActivityAuditAction.SEARCH_AUDIT,
        organisation_id=uuid4(),
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyActivityAuditAdministrationService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyActivityAuditAdministrationService.build_request(
        context,
        action=CompanyActivityAuditAction.REQUEST_AUDIT_EXPORT,
        filters={"actor": "admin"},
        export_format="csv",
    )
    result = CompanyActivityAuditAdministrationService.execute(context, request, executor)
    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyActivityAuditAdministrationService.build_request(
            context, action=CompanyActivityAuditAction.SEARCH_ACTIVITY
        )
