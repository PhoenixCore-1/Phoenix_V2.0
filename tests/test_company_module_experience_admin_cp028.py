from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.module_experience_admin import (
    CompanyModuleExperienceAction,
    CompanyModuleExperienceAdministrationRequest,
    CompanyModuleExperienceAdministrationResult,
    CompanyModuleExperienceAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyModuleExperienceAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            module_code=request.module_code,
            workspace_id=request.workspace_id,
            success=True,
        )


def context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = context()
    request = CompanyModuleExperienceAdministrationService.build_request(
        ctx,
        action=CompanyModuleExperienceAction.SET_MODULE_VISIBILITY,
        module_code="crm",
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.module_code = "production"


def test_module_code_is_required():
    ctx = context()
    request = CompanyModuleExperienceAdministrationRequest.create(
        ctx,
        action=CompanyModuleExperienceAction.SET_MODULE_VISIBILITY,
        module_code="   ",
    )
    with pytest.raises(ValueError, match="module code"):
        request.validate_for(ctx)


def test_workspace_actions_require_workspace_id():
    ctx = context()
    for action in (
        CompanyModuleExperienceAction.ENABLE_MODULE_IN_WORKSPACE,
        CompanyModuleExperienceAction.DISABLE_MODULE_IN_WORKSPACE,
    ):
        request = CompanyModuleExperienceAdministrationRequest.create(
            ctx, action=action, module_code="crm"
        )
        with pytest.raises(ValueError, match="workspace_id"):
            request.validate_for(ctx)


def test_presentation_actions_require_parameters():
    ctx = context()
    for action in (
        CompanyModuleExperienceAction.UPDATE_MODULE_NAVIGATION,
        CompanyModuleExperienceAction.UPDATE_MODULE_PRESENTATION,
        CompanyModuleExperienceAction.SET_MODULE_DEFAULT_VIEW,
    ):
        request = CompanyModuleExperienceAdministrationRequest.create(
            ctx, action=action, module_code="crm"
        )
        with pytest.raises(ValueError, match="parameters"):
            request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = context()
    request = CompanyModuleExperienceAdministrationRequest(
        action=CompanyModuleExperienceAction.SET_MODULE_VISIBILITY,
        organisation_id=uuid4(),
        module_code="crm",
    )
    with pytest.raises(PermissionError):
        CompanyModuleExperienceAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = context()
    executor = RecordingExecutor()
    request = CompanyModuleExperienceAdministrationService.build_request(
        ctx,
        action=CompanyModuleExperienceAction.UPDATE_MODULE_PRESENTATION,
        module_code="crm",
        parameters={"label": "Customer Management"},
    )
    result = CompanyModuleExperienceAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyModuleExperienceAdministrationService.build_request(
            ctx,
            action=CompanyModuleExperienceAction.SET_MODULE_VISIBILITY,
            module_code="crm",
        )
