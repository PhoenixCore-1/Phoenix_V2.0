from uuid import uuid4

import pytest

from phoenix_framework.company_platform.administration import (
    CompanyAdministrationService,
)
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import CompanyContext


def make_platform_context(organisation_id=None):
    return CompanyPlatformContext(
        FrameworkContext(
            request_id="cp002-test",
            identity_id=uuid4(),
            organisation_id=organisation_id or uuid4(),
            session_id=uuid4(),
            permissions=frozenset(),
            entitlements=frozenset(),
        )
    )


def test_company_view_projects_authoritative_core_company_context():
    organisation_id = uuid4()
    context = make_platform_context(organisation_id)
    company = CompanyContext(organisation_id=organisation_id, name="Example Company", active=True)

    view = CompanyAdministrationService.get_company_view(context, company)

    assert view.organisation_id == organisation_id
    assert view.name == "Example Company"
    assert view.active is True


def test_company_view_rejects_cross_tenant_company_context():
    context = make_platform_context(uuid4())
    company = CompanyContext(organisation_id=uuid4(), name="Other Company", active=True)

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyAdministrationService.get_company_view(context, company)


def test_company_view_requires_authenticated_tenant_context():
    organisation_id = uuid4()
    context = CompanyPlatformContext(
        FrameworkContext(
            request_id="cp002-test",
            identity_id=None,
            organisation_id=organisation_id,
            session_id=None,
            permissions=frozenset(),
            entitlements=frozenset(),
        )
    )
    company = CompanyContext(organisation_id=organisation_id, name="Example Company")

    with pytest.raises(PermissionError, match="Authenticated identity is required"):
        CompanyAdministrationService.get_company_view(context, company)
