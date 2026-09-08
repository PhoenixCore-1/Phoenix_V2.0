from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.workspace_assignments import (
    CompanyWorkspaceAssignmentAction,
    CompanyWorkspaceAssignmentRequest,
    CompanyWorkspaceAssignmentResult,
    CompanyWorkspaceAssignmentService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyWorkspaceAssignmentResult(
            action=request.action,
            organisation_id=request.organisation_id,
            target_id=request.workspace_id,
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


def test_assignment_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyWorkspaceAssignmentService.build_request(
        context,
        action=CompanyWorkspaceAssignmentAction.ASSIGN_WORKSPACE,
        identity_id=uuid4(),
        workspace_id=uuid4(),
        parameters={"reason": "role_default"},
    )
    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("reason", "role_default"),)
    with pytest.raises(FrozenInstanceError):
        request.workspace_id = uuid4()


def test_all_assignment_operations_require_identity_and_workspace():
    context = make_context()
    for action in CompanyWorkspaceAssignmentAction:
        request = CompanyWorkspaceAssignmentRequest(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=uuid4(),
            workspace_id=uuid4(),
        )
        request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyWorkspaceAssignmentRequest(
        action=CompanyWorkspaceAssignmentAction.ASSIGN_WORKSPACE,
        organisation_id=uuid4(),
        identity_id=uuid4(),
        workspace_id=uuid4(),
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyWorkspaceAssignmentService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyWorkspaceAssignmentService.build_request(
        context,
        action=CompanyWorkspaceAssignmentAction.SET_DEFAULT_WORKSPACE,
        identity_id=uuid4(),
        workspace_id=uuid4(),
    )
    result = CompanyWorkspaceAssignmentService.execute(context, request, executor)
    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyWorkspaceAssignmentService.build_request(
            context,
            action=CompanyWorkspaceAssignmentAction.ASSIGN_WORKSPACE,
            identity_id=uuid4(),
            workspace_id=uuid4(),
        )
