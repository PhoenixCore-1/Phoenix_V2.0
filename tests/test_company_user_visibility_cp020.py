from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.user_visibility import (
    CompanyUserVisibilityAction,
    CompanyUserVisibilityAdministrationRequest,
    CompanyUserVisibilityAdministrationResult,
    CompanyUserVisibilityAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyUserVisibilityAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=request.identity_id,
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
    request = CompanyUserVisibilityAdministrationService.build_request(
        context,
        action=CompanyUserVisibilityAction.GRANT_USER_SCOPE,
        identity_id=uuid4(),
        resource="accounts",
        scope="assigned",
        parameters={"reason": "management"},
    )
    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("reason", "management"),)
    with pytest.raises(FrozenInstanceError):
        request.resource = "orders"


def test_grant_and_set_visibility_require_scope():
    context = make_context()
    for action in (
        CompanyUserVisibilityAction.GRANT_USER_SCOPE,
        CompanyUserVisibilityAction.SET_USER_VISIBILITY,
    ):
        request = CompanyUserVisibilityAdministrationRequest.create(
            context,
            action=action,
            identity_id=uuid4(),
            resource="accounts",
        )
        with pytest.raises(ValueError, match="requires a scope"):
            request.validate_for(context)


def test_resource_and_identity_are_required():
    context = make_context()
    for action in CompanyUserVisibilityAction:
        request = CompanyUserVisibilityAdministrationRequest(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=uuid4(),
            resource="",
            scope="assigned",
        )
        with pytest.raises(ValueError, match="requires a resource"):
            request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyUserVisibilityAdministrationRequest(
        action=CompanyUserVisibilityAction.REVOKE_USER_SCOPE,
        organisation_id=uuid4(),
        identity_id=uuid4(),
        resource="accounts",
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyUserVisibilityAdministrationService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyUserVisibilityAdministrationService.build_request(
        context,
        action=CompanyUserVisibilityAction.SET_USER_VISIBILITY,
        identity_id=uuid4(),
        resource="accounts",
        scope="team",
    )
    result = CompanyUserVisibilityAdministrationService.execute(context, request, executor)
    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyUserVisibilityAdministrationService.build_request(
            context,
            action=CompanyUserVisibilityAction.GRANT_USER_SCOPE,
            identity_id=uuid4(),
            resource="accounts",
            scope="assigned",
        )
