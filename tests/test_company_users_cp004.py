from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.users import CompanyUserAdministrationService
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import UserContext


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


def test_user_view_projects_authoritative_core_user_context():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    user = UserContext(
        identity_id=uuid4(),
        username="jane",
        display_name="Jane Example",
        organisation_id=organisation_id,
        permissions=frozenset({"users.view"}),
        entitlements=frozenset({"platform.standard"}),
    )

    view = CompanyUserAdministrationService.get_user_view(context, user)

    assert view.identity_id == user.identity_id
    assert view.username == "jane"
    assert view.display_name == "Jane Example"
    assert view.organisation_id == organisation_id
    assert view.permissions == frozenset({"users.view"})
    assert view.entitlements == frozenset({"platform.standard"})


def test_user_view_rejects_cross_tenant_user():
    context = make_context(uuid4())
    user = UserContext(
        identity_id=uuid4(),
        username="other",
        display_name="Other User",
        organisation_id=uuid4(),
    )

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyUserAdministrationService.get_user_view(context, user)


def test_users_view_projects_only_current_tenant_users():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    users = (
        UserContext(uuid4(), "one", "User One", organisation_id),
        UserContext(uuid4(), "two", "User Two", organisation_id),
    )

    view = CompanyUserAdministrationService.get_users_view(context, users)

    assert view.organisation_id == organisation_id
    assert [user.username for user in view.users] == ["one", "two"]


def test_user_view_requires_authenticated_tenant_context():
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
    user = UserContext(uuid4(), "jane", "Jane Example", organisation_id)

    with pytest.raises(PermissionError):
        CompanyUserAdministrationService.get_user_view(context, user)
