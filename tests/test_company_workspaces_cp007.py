from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.workspaces import (
    CompanyWorkspaceAdministrationService,
    WorkspaceView,
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


def make_workspace(organisation_id):
    return WorkspaceView(
        workspace_id=uuid4(),
        name="Sales Workspace",
        navigation_keys=("company.dashboard", "company.users"),
        dashboard_keys=("sales.pipeline",),
        default_workspace=True,
        organisation_id=organisation_id,
    )


def test_workspace_view_projects_core_configuration():
    organisation_id = uuid4()
    context = make_context(organisation_id)

    view = CompanyWorkspaceAdministrationService.get_workspace_view(
        context,
        workspace_id=uuid4(),
        name="Sales Workspace",
        navigation_keys=("company.dashboard", "company.users"),
        dashboard_keys=("sales.pipeline",),
        default_workspace=True,
        organisation_id=organisation_id,
    )

    assert view.organisation_id == organisation_id
    assert view.name == "Sales Workspace"
    assert view.navigation_keys == ("company.dashboard", "company.users")
    assert view.dashboard_keys == ("sales.pipeline",)
    assert view.default_workspace is True


def test_workspace_view_rejects_cross_tenant_workspace():
    context = make_context(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyWorkspaceAdministrationService.get_workspace_view(
            context,
            workspace_id=uuid4(),
            name="Other Workspace",
            navigation_keys=(),
            dashboard_keys=(),
            default_workspace=False,
            organisation_id=uuid4(),
        )


def test_workspaces_view_rejects_cross_tenant_workspace():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    other_workspace = make_workspace(uuid4())

    with pytest.raises(PermissionError, match="does not match request organisation"):
        CompanyWorkspaceAdministrationService.get_workspaces_view(
            context, (other_workspace,)
        )


def test_workspaces_view_projects_current_tenant_workspaces():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    workspace = make_workspace(organisation_id)

    view = CompanyWorkspaceAdministrationService.get_workspaces_view(
        context, (workspace,)
    )

    assert view.organisation_id == organisation_id
    assert view.workspaces == (workspace,)


def test_workspace_view_requires_authenticated_tenant_context():
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
        CompanyWorkspaceAdministrationService.get_workspaces_view(context, ())
