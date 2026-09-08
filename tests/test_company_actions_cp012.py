from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.actions import (
    CompanyAdministrationAction,
    CompanyAdministrationRequest,
    CompanyAdministrationResult,
    CompanyAdministrationService,
)
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.context import FrameworkContext


def make_context(organisation_id, identity_id=None):
    request = RequestContext(
        request_id=str(uuid4()),
        identity_id=identity_id if identity_id is not None else uuid4(),
        organisation_id=organisation_id,
        session_id=uuid4(),
    )
    return CompanyPlatformContext(FrameworkContext.from_core(request))


def test_build_request_is_tenant_bound_and_immutable():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    request = CompanyAdministrationService.build_request(
        context,
        action=CompanyAdministrationAction.USER_ADMINISTRATION,
        target_id=uuid4(),
        parameters={"status": "ACTIVE", "note": "approved"},
    )

    assert request.organisation_id == organisation_id
    assert request.action is CompanyAdministrationAction.USER_ADMINISTRATION
    assert request.parameters == (("note", "approved"), ("status", "ACTIVE"))
    with pytest.raises(AttributeError):
        request.organisation_id = uuid4()


def test_request_rejects_cross_tenant_execution():
    owner = uuid4()
    request = CompanyAdministrationService.build_request(
        make_context(owner),
        action=CompanyAdministrationAction.ROLE_PERMISSION_ADMINISTRATION,
    )

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyAdministrationService.execute(
            make_context(uuid4()), request, RejectingExecutor()
        )


def test_execute_delegates_to_authoritative_executor():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    target_id = uuid4()
    request = CompanyAdministrationService.build_request(
        context,
        action=CompanyAdministrationAction.WORKSPACE_ADMINISTRATION,
        target_id=target_id,
    )
    executor = RecordingExecutor()

    result = CompanyAdministrationService.execute(context, request, executor)

    assert result.success is True
    assert result.organisation_id == organisation_id
    assert result.target_id == target_id
    assert executor.request is request


def test_unauthenticated_context_cannot_build_request():
    organisation_id = uuid4()
    request = RequestContext(
        request_id=str(uuid4()),
        identity_id=None,
        organisation_id=organisation_id,
        session_id=None,
    )
    context = CompanyPlatformContext(FrameworkContext.from_core(request))

    with pytest.raises(PermissionError):
        CompanyAdministrationService.build_request(
            context,
            action=CompanyAdministrationAction.DATA_VISIBILITY_ADMINISTRATION,
        )


class RecordingExecutor:
    def __init__(self):
        self.request = None

    def execute(self, context, request):
        self.request = request
        return CompanyAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=request.target_id,
            success=True,
            message="Delegated to Core application boundary",
        )


class RejectingExecutor:
    def execute(self, context, request):
        raise AssertionError("Cross-tenant request must be rejected before execution")
