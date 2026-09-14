"""Tests for the Company Platform HTTP read surface."""

from uuid import uuid4


def test_company_platform_router_defines_expected_read_routes():
    from phoenix_core.http_api.company import router

    paths = {route.path for route in router.routes}

    assert "/api/v1/company" in paths
    assert "/api/v1/company/users" in paths
    assert "/api/v1/company/memberships" in paths
    assert "/api/v1/company/roles" in paths
    assert "/api/v1/company/permissions" in paths


def test_company_platform_route_paths_are_tenant_scoped():
    from phoenix_core.http_api.company import router

    for route in router.routes:
        assert "{organisation_id}" not in route.path
        assert str(uuid4()) not in route.path
