from uuid import uuid4

import pytest

from phoenix_core.security.context import RequestContext
from phoenix_framework.company_platform.access import CompanyAccessService
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.contracts.navigation import NavigationContract


def context(permissions=frozenset(), entitlements=frozenset()):
    organisation_id = uuid4()
    return CompanyPlatformContext.from_core(RequestContext(uuid4(), identity_id=uuid4(), organisation_id=organisation_id, session_id=uuid4(), permissions=permissions, entitlements=entitlements))


def test_can_access_uses_core_derived_permission_context():
    assert CompanyAccessService.can_access(context(frozenset({"company.users"})), "company.users")
    assert not CompanyAccessService.can_access(context(), "company.users")


def test_require_access_rejects_missing_permission():
    with pytest.raises(PermissionError, match="company.roles_permissions"):
        CompanyAccessService.require_access(context(), "company.roles_permissions")


def test_require_access_accepts_permission():
    CompanyAccessService.require_access(context(frozenset({"company.roles_permissions"})), "company.roles_permissions")


def test_capability_evaluation_is_immutable_and_does_not_grant_access():
    result = CompanyAccessService.evaluate_capabilities(context(frozenset({"company.users"})), ("company.users", "company.audit"))
    assert result[0].permitted is True
    assert result[1].permitted is False
    with pytest.raises(TypeError):
        result[0].permitted = False


def test_navigation_filter_uses_permission_and_entitlement_context():
    items = (
        NavigationContract("users", "Users", "/users", permission="company.users"),
        NavigationContract("crm", "CRM", "/crm", entitlement="crm"),
        NavigationContract("billing", "Billing", "/billing", entitlement="billing"),
    )
    result = CompanyAccessService.filter_navigation(context(frozenset({"company.users"}), frozenset({"crm"})), items)
    assert [item.key for item in result] == ["users", "crm"]


def test_access_requires_authenticated_tenant_context():
    raw = RequestContext(uuid4())
    with pytest.raises(PermissionError):
        CompanyAccessService.can_access(CompanyPlatformContext.from_core(raw), "company.users")
