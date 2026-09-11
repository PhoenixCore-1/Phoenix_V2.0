from uuid import uuid4

from phoenix_core.api.application import CoreApi
from phoenix_core.api.context import RequestContextResolver
from phoenix_core.api.integration.contracts import IntegrationRequest
from phoenix_core.api.integration.service import CoreIntegrationService
from phoenix_core.api.platform_destination import (
    COMPANY_PLATFORM_ACCESS,
    PlatformDestination,
    SYSTEM_PLATFORM_ACCESS,
)
from phoenix_core.security.context import RequestContext


class FakeContextResolver:
    def __init__(self, context):
        self.context = context

    def resolve(self, **_kwargs):
        return self.context


def make_api(permissions=frozenset()):
    context = RequestContext(
        request_id="req-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=permissions,
        entitlements=frozenset({"production"}),
    )
    api = CoreApi(db=None, core_service=None)
    api.context_resolver = FakeContextResolver(context)
    return api, context


def test_system_platform_capability_wins():
    api, context = make_api(frozenset({SYSTEM_PLATFORM_ACCESS, COMPANY_PLATFORM_ACCESS}))

    response = api.resolve_platform_destination(
        request_id="req-1",
        session_id=context.session_id,
        organisation_id=context.organisation_id,
    )

    assert response.data["destination"] == PlatformDestination.SYSTEM_PLATFORM.value


def test_company_platform_capability_routes_to_company_platform():
    api, context = make_api(frozenset({COMPANY_PLATFORM_ACCESS}))

    response = api.resolve_platform_destination(
        request_id="req-1",
        session_id=context.session_id,
        organisation_id=context.organisation_id,
    )

    assert response.data["destination"] == PlatformDestination.COMPANY_PLATFORM.value


def test_normal_organisation_user_routes_to_user_platform():
    api, context = make_api()

    response = api.resolve_platform_destination(
        request_id="req-1",
        session_id=context.session_id,
        organisation_id=context.organisation_id,
    )

    assert response.data["destination"] == PlatformDestination.USER_PLATFORM.value


def test_integration_operation_resolves_destination_through_core():
    api, context = make_api(frozenset({COMPANY_PLATFORM_ACCESS}))
    integration = CoreIntegrationService(api)

    response = integration.handle(
        IntegrationRequest(
            request_id="req-1",
            operation="platform.destination.resolve",
            session_id=context.session_id,
            organisation_id=context.organisation_id,
        )
    )

    assert response.success is True
    assert response.data["destination"] == PlatformDestination.COMPANY_PLATFORM.value


def test_integration_operation_requires_session_and_organisation():
    api, _ = make_api()
    integration = CoreIntegrationService(api)

    request = IntegrationRequest(
        request_id="req-1",
        operation="platform.destination.resolve",
    )

    try:
        integration.handle(request)
    except Exception as exc:
        assert "authenticated session" in str(exc)
    else:
        raise AssertionError("Missing authentication context must be rejected")
