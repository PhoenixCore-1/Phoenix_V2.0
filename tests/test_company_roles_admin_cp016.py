from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.roles_admin import CompanyRoleAction, CompanyRoleAdministrationService


def make_context():
    organisation_id = uuid4()
    return CompanyPlatformContext.from_core(RequestContext(uuid4(), identity_id=uuid4(), organisation_id=organisation_id, session_id=uuid4(), permissions=frozenset({"company.roles_permissions"})))


class RecordingExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, context, request):
        self.calls.append((context, request))
        return request.action


def test_create_role_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.CREATE_ROLE, parameters={"name": "Sales Manager"})
    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("name", "Sales Manager"),)
    with pytest.raises(TypeError):
        request.role_id = uuid4()


def test_role_mutations_require_role_id():
    context = make_context()
    with pytest.raises(ValueError):
        CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.UPDATE_ROLE)


def test_permission_mutations_require_permission_code():
    context = make_context()
    with pytest.raises(ValueError):
        CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.GRANT_PERMISSION, role_id=uuid4())


def test_permission_mutation_delegates_to_authoritative_executor():
    context = make_context()
    request = CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.GRANT_PERMISSION, role_id=uuid4(), permission_code="company.users")
    executor = RecordingExecutor()
    assert CompanyRoleAdministrationService.execute(context, request, executor) == CompanyRoleAction.GRANT_PERMISSION
    assert executor.calls == [(context, request)]


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.CREATE_ROLE)
    foreign_context = CompanyPlatformContext.from_core(RequestContext(uuid4(), identity_id=uuid4(), organisation_id=uuid4(), session_id=uuid4(), permissions=frozenset({"company.roles_permissions"})))
    with pytest.raises(PermissionError):
        CompanyRoleAdministrationService.execute(foreign_context, request, RecordingExecutor())


def test_unauthenticated_context_cannot_build_role_request():
    context = CompanyPlatformContext.from_core(RequestContext(uuid4()))
    with pytest.raises(PermissionError):
        CompanyRoleAdministrationService.build_request(context, action=CompanyRoleAction.CREATE_ROLE)
