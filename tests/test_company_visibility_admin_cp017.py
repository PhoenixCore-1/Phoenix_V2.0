from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.visibility_admin import (
    CompanyVisibilityAction,
    CompanyVisibilityAdministrationRequest,
    CompanyVisibilityAdministrationResult,
    CompanyVisibilityAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyVisibilityAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=request.rule_id,
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


def test_build_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyVisibilityAdministrationService.build_request(
        context,
        action=CompanyVisibilityAction.CREATE_RULE,
        resource_scope="accounts",
        parameters={"scope": "own"},
    )

    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("scope", "own"),)
    with pytest.raises(FrozenInstanceError):
        request.rule_id = uuid4()


def test_existing_rule_operations_require_rule_id():
    context = make_context()
    for action in (
        CompanyVisibilityAction.UPDATE_RULE,
        CompanyVisibilityAction.ENABLE_RULE,
        CompanyVisibilityAction.DISABLE_RULE,
        CompanyVisibilityAction.ADD_ROLE_SCOPE,
        CompanyVisibilityAction.REMOVE_ROLE_SCOPE,
        CompanyVisibilityAction.UPDATE_RESOURCE_SCOPE,
    ):
        request = CompanyVisibilityAdministrationRequest.create(
            context,
            action=action,
            role_scope="manager" if action in {
                CompanyVisibilityAction.ADD_ROLE_SCOPE,
                CompanyVisibilityAction.REMOVE_ROLE_SCOPE,
            } else None,
            resource_scope="accounts" if action in {
                CompanyVisibilityAction.UPDATE_RULE,
                CompanyVisibilityAction.UPDATE_RESOURCE_SCOPE,
            } else None,
        )
        with pytest.raises(ValueError, match="rule_id"):
            request.validate_for(context)


def test_role_scope_operations_require_role_scope():
    context = make_context()
    for action in (CompanyVisibilityAction.ADD_ROLE_SCOPE, CompanyVisibilityAction.REMOVE_ROLE_SCOPE):
        request = CompanyVisibilityAdministrationRequest.create(
            context,
            action=action,
            rule_id=uuid4(),
        )
        with pytest.raises(ValueError, match="role_scope"):
            request.validate_for(context)


def test_resource_scope_operations_require_resource_scope():
    context = make_context()
    for action in (
        CompanyVisibilityAction.CREATE_RULE,
        CompanyVisibilityAction.UPDATE_RULE,
        CompanyVisibilityAction.UPDATE_RESOURCE_SCOPE,
    ):
        request = CompanyVisibilityAdministrationRequest.create(
            context,
            action=action,
            rule_id=uuid4() if action != CompanyVisibilityAction.CREATE_RULE else None,
        )
        with pytest.raises(ValueError, match="resource_scope"):
            request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyVisibilityAdministrationRequest(
        action=CompanyVisibilityAction.ENABLE_RULE,
        organisation_id=uuid4(),
        rule_id=uuid4(),
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyVisibilityAdministrationService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyVisibilityAdministrationService.build_request(
        context,
        action=CompanyVisibilityAction.ENABLE_RULE,
        rule_id=uuid4(),
    )

    result = CompanyVisibilityAdministrationService.execute(context, request, executor)

    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyVisibilityAdministrationService.build_request(
            context,
            action=CompanyVisibilityAction.CREATE_RULE,
            resource_scope="accounts",
        )
