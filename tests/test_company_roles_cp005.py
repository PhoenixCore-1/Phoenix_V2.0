from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.roles import (
    CompanyPermissionView,
    CompanyRoleView,
    CompanyRolesPermissionsService,
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


def test_role_view_projects_core_role_data():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    role_id = uuid4()

    view = CompanyRolesPermissionsService.get_role_view(
        context,
        role_id=role_id,
        name="Company Admin",
        description="Tenant administrator",
        permissions=frozenset({"users.view", "roles.view"}),
        organisation_id=organisation_id,
    )

    assert view.role_id == role_id
    assert view.name == "Company Admin"
    assert view.permissions == frozenset({"users.view", "roles.view"})
    assert view.organisation_id == organisation_id


def test_role_view_rejects_cross_tenant_role():
    context = make_context(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyRolesPermissionsService.get_role_view(
            context,
            role_id=uuid4(),
            name="Other Admin",
            description="Other tenant",
            permissions=frozenset(),
            organisation_id=uuid4(),
        )


def test_roles_permissions_view_rejects_cross_tenant_role():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    other_role = CompanyRoleView(
        role_id=uuid4(),
        name="Other",
        description="Other tenant",
        permissions=frozenset(),
        organisation_id=uuid4(),
    )

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyRolesPermissionsService.get_roles_permissions_view(
            context,
            roles=(other_role,),
            permissions=(CompanyPermissionView("users.view", "View users", "View tenant users"),),
        )


def test_roles_permissions_view_projects_current_tenant_data():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    role = CompanyRoleView(
        role_id=uuid4(),
        name="Manager",
        description="Tenant manager",
        permissions=frozenset({"users.view"}),
        organisation_id=organisation_id,
    )
    permission = CompanyPermissionView("users.view", "View users", "View tenant users")

    view = CompanyRolesPermissionsService.get_roles_permissions_view(
        context, roles=(role,), permissions=(permission,)
    )

    assert view.organisation_id == organisation_id
    assert view.roles == (role,)
    assert view.permissions == (permission,)


def test_role_view_requires_authenticated_tenant_context():
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
        CompanyRolesPermissionsService.get_role_view(
            context,
            role_id=uuid4(),
            name="Admin",
            description="Administrator",
            permissions=frozenset(),
            organisation_id=organisation_id,
        )
