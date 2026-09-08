from datetime import datetime, timezone
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.notifications import (
    CompanyNotificationItem,
    CompanyNotificationsService,
)
from phoenix_framework.context import FrameworkContext


def make_context(*, organisation_id=None, identity_id=None):
    request = RequestContext(
        request_id=str(uuid4()),
        identity_id=identity_id,
        organisation_id=organisation_id,
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    return CompanyPlatformContext(FrameworkContext.from_core(request))


def make_item(organisation_id, *, read=False):
    return CompanyNotificationItem(
        notification_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        title="Action required",
        message="A company task needs attention.",
        category="company",
        severity="info",
        recipient_identity_id=uuid4(),
        read=read,
        source="core",
        organisation_id=organisation_id,
    )


def test_notification_projects_authoritative_tenant_data():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id, identity_id=uuid4())

    item = CompanyNotificationsService.get_notification_item(
        context,
        notification_id=uuid4(),
        created_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        title="Action required",
        message="Please review this item.",
        category="company",
        severity="warning",
        recipient_identity_id=uuid4(),
        read=False,
        source="core",
        organisation_id=organisation_id,
        action_route="/company/tasks/1",
    )

    assert item.organisation_id == organisation_id
    assert item.read is False
    assert item.source == "core"


def test_cross_tenant_notification_is_rejected():
    context = make_context(organisation_id=uuid4(), identity_id=uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyNotificationsService.get_notification_item(
            context,
            notification_id=uuid4(),
            created_at=datetime.now(timezone.utc),
            title="Cross tenant",
            message="Should not be visible.",
            category="company",
            severity="info",
            recipient_identity_id=uuid4(),
            read=False,
            source="core",
            organisation_id=uuid4(),
        )


def test_notification_collection_rejects_cross_tenant_item():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id, identity_id=uuid4())

    with pytest.raises(PermissionError):
        CompanyNotificationsService.get_notifications_view(
            context, (make_item(uuid4()),)
        )


def test_unread_count_is_derived_from_projection():
    organisation_id = uuid4()
    context = make_context(organisation_id=organisation_id, identity_id=uuid4())
    items = (make_item(organisation_id), make_item(organisation_id, read=True), make_item(organisation_id))

    view = CompanyNotificationsService.get_notifications_view(context, items)

    assert view.unread_count == 2


def test_notification_projection_is_immutable():
    organisation_id = uuid4()
    item = make_item(organisation_id)

    with pytest.raises(Exception):
        item.read = True


def test_notification_view_requires_authenticated_tenant_context():
    context = make_context(organisation_id=uuid4(), identity_id=None)

    with pytest.raises(PermissionError):
        CompanyNotificationsService.get_notifications_view(context, ())
