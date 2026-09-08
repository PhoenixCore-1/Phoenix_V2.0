from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.navigation import CompanyNavigationService
from phoenix_framework.company_platform.workspaces import WorkspaceView
from phoenix_framework.contracts.navigation import NavigationContract


def make_context(organisation_id, permissions=frozenset(), entitlements=frozenset(), identity_id=None):
    core = RequestContext(uuid4(), identity_id=identity_id or uuid4(), organisation_id=organisation_id, session_id=uuid4(), permissions=permissions, entitlements=entitlements)
    return CompanyPlatformContext.from_core(core)


def test_navigation_filters_permission_and_entitlement():
    organisation_id = uuid4()
    context = make_context(organisation_id, permissions=frozenset({"company.view"}), entitlements=frozenset({"crm"}))
    navigation = (
        NavigationContract("open", "Open", "/open", permission="company.view", order=2),
        NavigationContract("restricted", "Restricted", "/restricted", permission="company.admin", order=1),
        NavigationContract("crm", "CRM", "/crm", entitlement="crm", order=3),
        NavigationContract("billing", "Billing", "/billing", entitlement="billing", order=4),
        NavigationContract("disabled", "Disabled", "/disabled", enabled=False, order=0),
    )
    result = CompanyNavigationService.resolve_navigation(context, navigation=navigation)
    assert [item.key for item in result.items] == ["open", "crm"]


def test_workspace_limits_navigation():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    workspace = WorkspaceView(uuid4(), "Sales", ("crm",), (), False, organisation_id)
    navigation = (NavigationContract("crm", "CRM", "/crm"), NavigationContract("other", "Other", "/other"))
    result = CompanyNavigationService.resolve_navigation(context, navigation=navigation, workspace=workspace)
    assert [item.key for item in result.items] == ["crm"]
    assert result.workspace_id == workspace.workspace_id


def test_cross_tenant_workspace_rejected():
    context = make_context(uuid4())
    workspace = WorkspaceView(uuid4(), "Other", ("crm",), (), False, uuid4())
    with pytest.raises(PermissionError):
        CompanyNavigationService.resolve_navigation(context, workspace=workspace)


def test_workspace_resolution_prefers_default():
    organisation_id = uuid4()
    context = make_context(organisation_id)
    first = WorkspaceView(uuid4(), "First", (), (), False, organisation_id)
    default = WorkspaceView(uuid4(), "Default", (), (), True, organisation_id)
    foreign = WorkspaceView(uuid4(), "Foreign", (), (), True, uuid4())
    assert CompanyNavigationService.resolve_workspace(context, (first, default, foreign)) == default


def test_navigation_requires_authenticated_tenant_context():
    context = CompanyPlatformContext.from_core(RequestContext(uuid4()))
    with pytest.raises(PermissionError):
        CompanyNavigationService.resolve_navigation(context)
