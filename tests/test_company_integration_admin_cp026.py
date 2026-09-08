from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.integration_admin import (
    CompanyIntegrationAction,
    CompanyIntegrationAdministrationRequest,
    CompanyIntegrationAdministrationResult,
    CompanyIntegrationAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyIntegrationAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            integration_key=request.integration_key,
            success=True,
        )


def context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = context()
    request = CompanyIntegrationAdministrationService.build_request(
        ctx, action=CompanyIntegrationAction.ENABLE_INTEGRATION, integration_key="sage"
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.integration_key = "other"


def test_integration_key_is_required():
    ctx = context()
    request = CompanyIntegrationAdministrationRequest.create(
        ctx, action=CompanyIntegrationAction.ENABLE_INTEGRATION, integration_key="   "
    )
    with pytest.raises(ValueError, match="integration key"):
        request.validate_for(ctx)


def test_configuration_and_connect_require_parameters():
    ctx = context()
    for action in (
        CompanyIntegrationAction.UPDATE_INTEGRATION_CONFIGURATION,
        CompanyIntegrationAction.CONNECT,
    ):
        request = CompanyIntegrationAdministrationRequest.create(
            ctx, action=action, integration_key="erp"
        )
        with pytest.raises(ValueError, match="configuration parameters"):
            request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = context()
    request = CompanyIntegrationAdministrationRequest(
        action=CompanyIntegrationAction.TEST_CONNECTION,
        organisation_id=uuid4(),
        integration_key="erp",
    )
    with pytest.raises(PermissionError):
        CompanyIntegrationAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = context()
    executor = RecordingExecutor()
    request = CompanyIntegrationAdministrationService.build_request(
        ctx,
        action=CompanyIntegrationAction.UPDATE_INTEGRATION_CONFIGURATION,
        integration_key="erp",
        parameters={"endpoint": "authoritative"},
    )
    result = CompanyIntegrationAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyIntegrationAdministrationService.build_request(
            ctx, action=CompanyIntegrationAction.ENABLE_INTEGRATION, integration_key="erp"
        )
