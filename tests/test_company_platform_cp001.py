from uuid import uuid4

import pytest

from phoenix_framework.company_platform import (
    COMPANY_PLATFORM_NAVIGATION,
    CompanyPlatformCapabilities,
    CompanyPlatformContract,
    CompanyPlatformContext,
)
from phoenix_framework.context import FrameworkContext


def test_company_platform_contract_is_framework_owned():
    contract = CompanyPlatformContract()

    assert contract.code == "company_platform"
    assert contract.version == "1.0.0"
    assert CompanyPlatformCapabilities.COMPANY_ADMINISTRATION in contract.capabilities
    assert CompanyPlatformCapabilities.USER_ADMINISTRATION in contract.capabilities
    assert CompanyPlatformCapabilities.REPORTING in contract.capabilities


def test_company_platform_navigation_is_platform_experience_not_business_module():
    assert len(COMPANY_PLATFORM_NAVIGATION) == 10
    assert all(item.module_code is None for item in COMPANY_PLATFORM_NAVIGATION)
    assert COMPANY_PLATFORM_NAVIGATION[0].route == "/company"


def test_company_platform_context_requires_identity_and_tenant():
    context = FrameworkContext(
        request_id="req-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )

    CompanyPlatformContext(context).require_access()


def test_company_platform_context_rejects_missing_tenant():
    context = FrameworkContext(
        request_id="req-2",
        identity_id=uuid4(),
        organisation_id=None,
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(),
    )

    with pytest.raises(PermissionError, match="Organisation context is required"):
        CompanyPlatformContext(context).require_access()


def test_company_platform_context_rejects_missing_identity():
    context = FrameworkContext(
        request_id="req-3",
        identity_id=None,
        organisation_id=uuid4(),
        session_id=None,
        permissions=frozenset(),
        entitlements=frozenset(),
    )

    with pytest.raises(PermissionError, match="Authenticated identity is required"):
        CompanyPlatformContext(context).require_access()
