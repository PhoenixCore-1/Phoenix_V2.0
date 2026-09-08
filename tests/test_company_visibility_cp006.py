from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.visibility import (
    DataVisibilityAdministrationService,
    DataVisibilityRuleView,
)
from phoenix_framework.context import FrameworkContext


def make_context(organisation_id):
    request = RequestContext(
        request_id=uuid4(),
        identity_id=uuid4(),
        organisation_id=organisation_id,
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )
    return CompanyPlatformContext(FrameworkContext.from_core(request))


def make_rule(organisation_id):
    return DataVisibilityRuleView(
        rule_id=uuid4(),
        name="Sales visibility",
        resource="sales.accounts",
        scope="assigned",
        allowed_roles=frozenset({"sales.manager"}),
        enabled=True,
        organisation_id=organisation_id,
    )


def test_visibility_rule_projects_core_data():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    view = DataVisibilityAdministrationService.get_rule_view(
        context,
        rule_id=uuid4(),
        name="Sales visibility",
        resource="sales.accounts",
        scope="assigned",
        allowed_roles=frozenset({"sales.manager"}),
        enabled=True,
        organisation_id=organisation_id,
    )

    assert view.organisation_id == organisation_id
    assert view.resource == "sales.accounts"
    assert view.scope == "assigned"
    assert view.allowed_roles == frozenset({"sales.manager"})


def test_visibility_rule_rejects_cross_tenant_data():
    context = make_context(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        DataVisibilityAdministrationService.get_rule_view(
            context,
            rule_id=uuid4(),
            name="Other tenant",
            resource="sales.accounts",
            scope="all",
            allowed_roles=frozenset(),
            enabled=True,
            organisation_id=uuid4(),
        )


def test_visibility_collection_rejects_cross_tenant_rule():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    other_rule = make_rule(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        DataVisibilityAdministrationService.get_visibility_view(context, (other_rule,))


def test_visibility_collection_projects_current_tenant_rules():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    rule = make_rule(organisation_id)

    view = DataVisibilityAdministrationService.get_visibility_view(context, (rule,))

    assert view.organisation_id == organisation_id
    assert view.rules == (rule,)


def test_visibility_requires_authenticated_tenant_context():
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
        DataVisibilityAdministrationService.get_visibility_view(context, ())
