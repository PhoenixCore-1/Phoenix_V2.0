from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.actions import CompanyAdministrationResult, CompanyUserAction, CompanyUserAdministrationRequest, CompanyUserAdministrationOperationService
from phoenix_framework.company_platform.context import CompanyPlatformContext


def make_context(organisation_id=None):
    organisation_id = organisation_id or uuid4()
    return CompanyPlatformContext.from_core(RequestContext(uuid4(), identity_id=uuid4(), organisation_id=organisation_id, session_id=uuid4(), permissions=frozenset({"company.users"})))


class RecordingExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, context, request):
        self.calls.append((context, request))
        return CompanyAdministrationResult(request.action, request.organisation_id, request.identity_id, True, "accepted")


def test_build_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyUserAdministrationOperationService.build_request(context, action=CompanyUserAction.INVITE, parameters={"email": "user@example.com"})
    assert request.organisation_id == context.organisation_id
    assert request.identity_id is None
    assert request.parameters == (("email", "user@example.com"),)
    with pytest.raises(TypeError):
        request.organisation_id = uuid4()


def test_existing_user_operations_require_identity():
    context = make_context()
    with pytest.raises(ValueError):
        CompanyUserAdministrationOperationService.build_request(context, action=CompanyUserAction.ACTIVATE)


def test_role_operations_require_role():
    context = make_context()
    with pytest.raises(ValueError):
        CompanyUserAdministrationOperationService.build_request(context, action=CompanyUserAction.ASSIGN_ROLE, identity_id=uuid4())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    request = CompanyUserAdministrationOperationService.build_request(context, action=CompanyUserAction.ACTIVATE, identity_id=uuid4())
    executor = RecordingExecutor()
    result = CompanyUserAdministrationOperationService.execute(context, request, executor)
    assert result.success is True
    assert executor.calls == [(context, request)]


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyUserAdministrationRequest(CompanyUserAction.ACTIVATE, uuid4(), uuid4())
    with pytest.raises(PermissionError):
        CompanyUserAdministrationOperationService.execute(context, request, RecordingExecutor())


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(uuid4()))
    with pytest.raises(PermissionError):
        CompanyUserAdministrationOperationService.build_request(context, action=CompanyUserAction.INVITE, parameters={"email": "user@example.com"})
