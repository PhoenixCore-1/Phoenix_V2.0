from datetime import datetime, timezone
from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.audit import CompanyAuditItem, CompanyAuditService
from phoenix_framework.company_platform.context import CompanyPlatformContext


def make_context(organisation_id, identity_id=None):
    core = RequestContext(
        request_id=uuid4(),
        identity_id=identity_id if identity_id is not None else uuid4(),
        organisation_id=organisation_id,
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    return CompanyPlatformContext.from_core(core)


def make_item(organisation_id):
    return CompanyAuditItem(
        audit_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
        action="user.login",
        resource="identity",
        resource_id="user-1",
        actor_identity_id=uuid4(),
        outcome="success",
        organisation_id=organisation_id,
    )


def test_audit_item_projects_core_record():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    item = CompanyAuditService.get_audit_item(
        context,
        audit_id=uuid4(),
        occurred_at=datetime(2026, 9, 8, tzinfo=timezone.utc),
        action="user.login",
        resource="identity",
        resource_id="user-1",
        actor_identity_id=None,
        outcome="success",
        organisation_id=organisation_id,
    )

    assert item.organisation_id == organisation_id
    assert item.action == "user.login"
    assert item.outcome == "success"


def test_cross_tenant_audit_record_is_rejected():
    context = make_context(uuid4())

    with pytest.raises(PermissionError):
        CompanyAuditService.get_audit_item(
            context,
            audit_id=uuid4(),
            occurred_at=datetime.now(timezone.utc),
            action="user.login",
            resource="identity",
            resource_id=None,
            actor_identity_id=None,
            outcome="success",
            organisation_id=uuid4(),
        )


def test_audit_view_rejects_cross_tenant_record():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    with pytest.raises(PermissionError):
        CompanyAuditService.get_audit_view(context, (make_item(uuid4()),))


def test_audit_view_requires_authenticated_context():
    organisation_id = uuid4()
    context = make_context(organisation_id, identity_id=None)

    with pytest.raises(PermissionError):
        CompanyAuditService.get_audit_view(context, ())
