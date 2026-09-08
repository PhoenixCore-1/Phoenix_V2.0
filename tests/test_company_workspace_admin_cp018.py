from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.workspaces_admin import (
    CompanyWorkspaceAction,
    CompanyWorkspaceAdministrationRequest,
    CompanyWorkspaceAdministrationResult,
    CompanyWorkspaceAdministrationOperationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyWorkspaceAdministrationResult(
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


def test_build_request_is_tenant_bound_and_immutable():
    context = make_context()
    request = CompanyWorkspaceAdministrationOperationService.build_request(
        context,
        action=CompanyWorkspaceAction.CREATE_WORKSPACE,
        parameters={"name": "Sales"},
    )
    assert request.organisation_id == context.organisation_id
    assert request.parameters == (("name", "Sales"),)
    with pytest.raises(FrozenInstanceError):
        request.workspace_id = uuid4()


def test_existing_workspace_operations_require_workspace_id():
    context = make_context()
    for action in (
        CompanyWorkspaceAction.UPDATE_WORKSPACE,
        CompanyWorkspaceAction.ACTIVATE_WORKSPACE,
        CompanyWorkspaceAction.DEACTIVATE_WORKSPACE,
        CompanyWorkspaceAction.SET_DEFAULT_WORKSPACE,
        CompanyWorkspaceAction.UPDATE_NAVIGATION,
        CompanyWorkspaceAction.UPDATE_DASHBOARD,
    ):
        request = CompanyWorkspaceAdministrationRequest.create(
            context,
            action=action,
            parameters={"name": "Sales"} if action == CompanyWorkspaceAction.UPDATE_WORKSPACE else None,
            navigation_keys=("dashboard",) if action == CompanyWorkspaceAction.UPDATE_NAVIGATION else None,
            dashboard_keys=("overview",) if action == CompanyWorkspaceAction.UPDATE_DASHBOARD else None,
        )
        with pytest.raises(ValueError, match="workspace_id"):
            request.validate_for(context)


def test_navigation_and_dashboard_updates_require_keys():
    context = make_context()
    navigation_request = CompanyWorkspaceAdministrationRequest.create(
        context,
        action=CompanyWorkspaceAction.UPDATE_NAVIGATION,
        workspace_id=uuid4(),
    )
    with pytest.raises(ValueError, match="navigation_keys"):
        navigation_request.validate_for(context)

    dashboard_request = CompanyWorkspaceAdministrationRequest.create(
        context,
        action=CompanyWorkspaceAction.UPDATE_DASHBOARD,
        workspace_id=uuid4(),
    )
    with pytest.raises(ValueError, match="dashboard_keys"):
        dashboard_request.validate_for(context)


def test_create_and_update_require_workspace_parameters():
    context = make_context()
    create_request = CompanyWorkspaceAdministrationRequest.create(
        context, action=CompanyWorkspaceAction.CREATE_WORKSPACE
    )
    with pytest.raises(ValueError, match="workspace parameters"):
        create_request.validate_for(context)

    update_request = CompanyWorkspaceAdministrationRequest.create(
        context, action=CompanyWorkspaceAction.UPDATE_WORKSPACE, workspace_id=uuid4()
    )
    with pytest.raises(ValueError, match="workspace parameters"):
        update_request.validate_for(context)


def test_cross_tenant_request_is_rejected():
    context = make_context()
    request = CompanyWorkspaceAdministrationRequest(
        action=CompanyWorkspaceAction.ACTIVATE_WORKSPACE,
        organisation_id=uuid4(),
        workspace_id=uuid4(),
    )
    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyWorkspaceAdministrationOperationService.execute(context, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    context = make_context()
    executor = RecordingExecutor()
    request = CompanyWorkspaceAdministrationOperationService.build_request(
        context,
        action=CompanyWorkspaceAction.UPDATE_NAVIGATION,
        workspace_id=uuid4(),
        navigation_keys=("dashboard", "accounts"),
    )
    result = CompanyWorkspaceAdministrationOperationService.execute(context, request, executor)
    assert result.success is True
    assert executor.requests == [(context, request)]


def test_unauthenticated_context_cannot_build_request():
    context = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyWorkspaceAdministrationOperationService.build_request(
            context,
            action=CompanyWorkspaceAction.CREATE_WORKSPACE,
            parameters={"name": "Sales"},
        )
