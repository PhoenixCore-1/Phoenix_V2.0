from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.notifications_admin import (
    CompanyNotificationAction,
    CompanyNotificationAdministrationRequest,
    CompanyNotificationAdministrationResult,
    CompanyNotificationAdministrationService,
)


class RecordingExecutor:
    def __init__(self):
        self.requests = []

    def execute(self, context, request):
        self.requests.append((context, request))
        return CompanyNotificationAdministrationResult(
            action=request.action,
            organisation_id=request.organisation_id,
            identity_id=request.identity_id,
            notification_id=request.notification_id,
            success=True,
        )


def context():
    return CompanyPlatformContext.from_core(
        RequestContext(request_id=str(uuid4()), identity_id=uuid4(), organisation_id=uuid4())
    )


def test_request_is_tenant_bound_and_immutable():
    ctx = context()
    request = CompanyNotificationAdministrationService.build_request(
        ctx,
        action=CompanyNotificationAction.UPDATE_COMPANY_PREFERENCES,
        parameters={"email": "enabled"},
    )
    assert request.organisation_id == ctx.organisation_id
    with pytest.raises(FrozenInstanceError):
        request.identity_id = uuid4()


def test_user_and_notification_operations_require_targets():
    ctx = context()
    request = CompanyNotificationAdministrationRequest.create(
        ctx, action=CompanyNotificationAction.UPDATE_USER_PREFERENCES
    )
    with pytest.raises(ValueError, match="identity_id"):
        request.validate_for(ctx)

    request = CompanyNotificationAdministrationRequest.create(
        ctx, action=CompanyNotificationAction.MARK_READ, identity_id=uuid4()
    )
    with pytest.raises(ValueError, match="notification_id"):
        request.validate_for(ctx)


def test_preference_operations_validate_parameters():
    ctx = context()
    cases = (
        (CompanyNotificationAction.UPDATE_COMPANY_PREFERENCES, {}),
        (CompanyNotificationAction.UPDATE_USER_PREFERENCES, {}),
        (CompanyNotificationAction.ENABLE_CHANNEL, {}),
        (CompanyNotificationAction.DISABLE_CHANNEL, {}),
        (CompanyNotificationAction.ENABLE_NOTIFICATION_TYPE, {}),
        (CompanyNotificationAction.DISABLE_NOTIFICATION_TYPE, {}),
    )
    for action, parameters in cases:
        identity_id = uuid4() if action == CompanyNotificationAction.UPDATE_USER_PREFERENCES else None
        request = CompanyNotificationAdministrationRequest.create(
            ctx, action=action, identity_id=identity_id, parameters=parameters
        )
        with pytest.raises(ValueError):
            request.validate_for(ctx)


def test_send_notification_requires_recipient_and_parameters():
    ctx = context()
    request = CompanyNotificationAdministrationRequest.create(
        ctx, action=CompanyNotificationAction.SEND_NOTIFICATION
    )
    with pytest.raises(ValueError, match="identity_id"):
        request.validate_for(ctx)

    request = CompanyNotificationAdministrationRequest.create(
        ctx, action=CompanyNotificationAction.SEND_NOTIFICATION, identity_id=uuid4()
    )
    with pytest.raises(ValueError, match="notification parameters"):
        request.validate_for(ctx)


def test_cross_tenant_request_is_rejected():
    ctx = context()
    request = CompanyNotificationAdministrationRequest(
        action=CompanyNotificationAction.MARK_READ,
        organisation_id=uuid4(),
        identity_id=uuid4(),
        notification_id=uuid4(),
    )
    with pytest.raises(PermissionError):
        CompanyNotificationAdministrationService.execute(ctx, request, RecordingExecutor())


def test_execute_delegates_to_authoritative_executor():
    ctx = context()
    executor = RecordingExecutor()
    request = CompanyNotificationAdministrationService.build_request(
        ctx,
        action=CompanyNotificationAction.ENABLE_CHANNEL,
        parameters={"channel": "email"},
    )
    result = CompanyNotificationAdministrationService.execute(ctx, request, executor)
    assert result.success
    assert executor.requests == [(ctx, request)]


def test_unauthenticated_context_cannot_build_request():
    ctx = CompanyPlatformContext.from_core(RequestContext(request_id=str(uuid4())))
    with pytest.raises(PermissionError):
        CompanyNotificationAdministrationService.build_request(
            ctx, action=CompanyNotificationAction.UPDATE_COMPANY_PREFERENCES,
            parameters={"email": "enabled"},
        )
