from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.workflow_admin import (
    CompanyWorkflowAction,
    CompanyWorkflowAdministrationRequest,
    CompanyWorkflowAdministrationResult,
    CompanyWorkflowAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyWorkflowAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            workflow_key=request.workflow_key,
            target_id=request.target_id,
            success=True,
        )


def context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = context()
    request = CompanyWorkflowAdministrationService.build_request(
        ctx, action=CompanyWorkflowAction.ENABLE_WORKFLOW, workflow_key="order_approval"
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.workflow_key = "other"


def test_workflow_key_is_required():
    ctx = context()
    request = CompanyWorkflowAdministrationRequest.create(
        ctx, action=CompanyWorkflowAction.ENABLE_WORKFLOW, workflow_key="   "
    )
    with pytest.raises(ValueError, match="workflow key"):
        request.validate_for(ctx)


def test_target_actions_require_target_id():
    ctx = context()
    for action in (
        CompanyWorkflowAction.ASSIGN_WORKFLOW,
        CompanyWorkflowAction.UNASSIGN_WORKFLOW,
        CompanyWorkflowAction.START_WORKFLOW,
        CompanyWorkflowAction.PAUSE_WORKFLOW,
        CompanyWorkflowAction.RESUME_WORKFLOW,
        CompanyWorkflowAction.CANCEL_WORKFLOW,
    ):
        request = CompanyWorkflowAdministrationRequest.create(
            ctx, action=action, workflow_key="order_approval"
        )
        with pytest.raises(ValueError, match="target_id"):
            request.validate_for(ctx)


def test_configuration_update_requires_parameters():
    ctx = context()
    request = CompanyWorkflowAdministrationRequest.create(
        ctx,
        action=CompanyWorkflowAction.UPDATE_WORKFLOW_CONFIGURATION,
        workflow_key="order_approval",
    )
    with pytest.raises(ValueError, match="parameters"):
        request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = context()
    request = CompanyWorkflowAdministrationRequest(
        action=CompanyWorkflowAction.START_WORKFLOW,
        organisation_id=uuid4(),
        workflow_key="order_approval",
        target_id="order-1",
    )
    with pytest.raises(PermissionError):
        CompanyWorkflowAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = context()
    executor = RecordingExecutor()
    request = CompanyWorkflowAdministrationService.build_request(
        ctx,
        action=CompanyWorkflowAction.ASSIGN_WORKFLOW,
        workflow_key="order_approval",
        target_id="order-1",
    )
    result = CompanyWorkflowAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyWorkflowAdministrationService.build_request(
            ctx, action=CompanyWorkflowAction.ENABLE_WORKFLOW, workflow_key="order_approval"
        )
