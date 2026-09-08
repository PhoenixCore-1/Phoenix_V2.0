from uuid import uuid4

import pytest

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.dashboard import (
    CompanyDashboardService,
    CompanyDashboardSnapshot,
)
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import CompanyContext, ModuleDescriptor


def make_context(organisation_id):
    return CompanyPlatformContext(
        FrameworkContext(
            request_id="cp003-test",
            identity_id=uuid4(),
            organisation_id=organisation_id,
            session_id=uuid4(),
            permissions=frozenset(),
            entitlements=frozenset(),
        )
    )


def test_dashboard_projects_authoritative_company_and_snapshot():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    company = CompanyContext(organisation_id=organisation_id, name="Acme", active=True)
    module = ModuleDescriptor(code="sales", name="Sales", version="1.0.0")
    snapshot = CompanyDashboardSnapshot(
        user_count=12,
        active_user_count=9,
        activity_count=42,
        visible_modules=(module,),
        attention_items=("Review inactive users",),
    )

    view = CompanyDashboardService.get_dashboard_view(context, company, snapshot)

    assert view.organisation_id == organisation_id
    assert view.company_name == "Acme"
    assert view.user_count == 12
    assert view.active_user_count == 9
    assert view.activity_count == 42
    assert view.visible_modules == (module,)
    assert view.attention_items == ("Review inactive users",)


def test_dashboard_rejects_cross_tenant_company():
    context = make_context(uuid4())
    company = CompanyContext(organisation_id=uuid4(), name="Other", active=True)

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyDashboardService.get_dashboard_view(
            context, company, CompanyDashboardSnapshot()
        )


def test_dashboard_requires_authenticated_tenant_context():
    organisation_id = uuid4()
    context = CompanyPlatformContext(
        FrameworkContext(
            request_id="cp003-test",
            identity_id=None,
            organisation_id=organisation_id,
            session_id=None,
            permissions=frozenset(),
            entitlements=frozenset(),
        )
    )
    company = CompanyContext(organisation_id=organisation_id, name="Acme")

    with pytest.raises(PermissionError, match="Authenticated identity is required"):
        CompanyDashboardService.get_dashboard_view(
            context, company, CompanyDashboardSnapshot()
        )


def test_dashboard_snapshot_rejects_invalid_counts():
    with pytest.raises(ValueError):
        CompanyDashboardSnapshot(user_count=-1)

    with pytest.raises(ValueError):
        CompanyDashboardSnapshot(user_count=2, active_user_count=3)
