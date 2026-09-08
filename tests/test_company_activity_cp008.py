from datetime import datetime, timezone
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.activity import (
    CompanyActivityAdministrationService,
    CompanyActivityItem,
)
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.context import FrameworkContext


def make_context(organisation_id, identity_id=None):
    request = RequestContext(
        request_id=uuid4(),
        identity_id=identity_id if identity_id is not None else uuid4(),
        organisation_id=organisation_id,
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    return CompanyPlatformContext(FrameworkContext.from_core(request))


def make_item(organisation_id):
    return CompanyActivityItem(
        activity_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        category="user",
        summary="User signed in",
        actor_identity_id=uuid4(),
        source="core",
        organisation_id=organisation_id,
    )


def test_activity_item_projects_authoritative_activity():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    item = CompanyActivityAdministrationService.get_activity_item(
        context,
        activity_id=uuid4(),
        occurred_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        category="user",
        summary="User signed in",
        actor_identity_id=None,
        source="core",
        organisation_id=organisation_id,
    )

    assert item.organisation_id == organisation_id
    assert item.category == "user"
    assert item.source == "core"


def test_activity_item_rejects_cross_tenant_activity():
    context = make_context(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyActivityAdministrationService.get_activity_item(
            context,
            activity_id=uuid4(),
            occurred_at=datetime.now(timezone.utc),
            category="user",
            summary="Cross tenant event",
            actor_identity_id=None,
            source="core",
            organisation_id=uuid4(),
        )


def test_activity_view_rejects_cross_tenant_item():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyActivityAdministrationService.get_activity_view(
            context, (make_item(uuid4()),)
        )


def test_activity_view_requires_authenticated_context():
    organisation_id = uuid4()
    request = RequestContext(
        request_id=uuid4(),
        identity_id=None,
        organisation_id=organisation_id,
        session_id=None,
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    context = CompanyPlatformContext(FrameworkContext.from_core(request))

    with pytest.raises(PermissionError):
        CompanyActivityAdministrationService.get_activity_view(context, ())
