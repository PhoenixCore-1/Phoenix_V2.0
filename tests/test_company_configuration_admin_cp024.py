from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.configuration_admin import (
    CompanyConfigurationAction,
    CompanyConfigurationAdministrationRequest,
    CompanyConfigurationAdministrationResult,
    CompanyConfigurationAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyConfigurationAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            key=request.key,
            success=True,
        )


def context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = context()
    request = CompanyConfigurationAdministrationService.build_request(
        ctx, action=CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE,
        key="default_landing_page", value="dashboard"
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.value = "other"


def test_key_and_value_requirements_are_enforced():
    ctx = context()
    for action in (
        CompanyConfigurationAction.SET_COMPANY_DEFAULT,
        CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE,
        CompanyConfigurationAction.RESET_COMPANY_PREFERENCE,
    ):
        request = CompanyConfigurationAdministrationRequest.create(ctx, action=action)
        with pytest.raises(ValueError, match="key"):
            request.validate_for(ctx)

    request = CompanyConfigurationAdministrationRequest.create(
        ctx, action=CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE, key="theme"
    )
    with pytest.raises(ValueError, match="value"):
        request.validate_for(ctx)


def test_presentation_feature_requires_feature_key():
    ctx = context()
    request = CompanyConfigurationAdministrationRequest.create(
        ctx, action=CompanyConfigurationAction.ENABLE_PRESENTATION_FEATURE
    )
    with pytest.raises(ValueError, match="feature key"):
        request.validate_for(ctx)


def test_format_configuration_requires_value():
    ctx = context()
    for action in (
        CompanyConfigurationAction.SET_COMPANY_LOCALE,
        CompanyConfigurationAction.SET_COMPANY_TIMEZONE,
        CompanyConfigurationAction.SET_COMPANY_DATE_FORMAT,
        CompanyConfigurationAction.SET_COMPANY_CURRENCY_FORMAT,
    ):
        request = CompanyConfigurationAdministrationRequest.create(ctx, action=action)
        with pytest.raises(ValueError, match="value"):
            request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = context()
    request = CompanyConfigurationAdministrationRequest(
        action=CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE,
        organisation_id=uuid4(), key="theme", value="dark"
    )
    with pytest.raises(PermissionError):
        CompanyConfigurationAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = context()
    executor = RecordingExecutor()
    request = CompanyConfigurationAdministrationService.build_request(
        ctx, action=CompanyConfigurationAction.SET_COMPANY_TIMEZONE,
        value="Africa/Johannesburg"
    )
    result = CompanyConfigurationAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyConfigurationAdministrationService.build_request(
            ctx, action=CompanyConfigurationAction.SET_COMPANY_LOCALE, value="en-ZA"
        )
