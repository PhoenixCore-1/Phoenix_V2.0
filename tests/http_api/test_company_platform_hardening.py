"""Regression coverage for the Company Platform hardening boundary."""

from uuid import UUID

from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.migration_runner import apply_all


def test_all_checked_in_migrations_install_company_platform_foundation(tmp_path):
    db = SQLiteDatabase(tmp_path / "core.db")
    apply_all(db)

    permission_rows = db.execute(
        "SELECT id, code FROM permissions WHERE code LIKE 'company.%' ORDER BY code"
    ).fetchall()
    assert len(permission_rows) == 8
    assert all(UUID(row["id"]) for row in permission_rows)
    assert {row["code"] for row in permission_rows} == {
        "company.activity.view",
        "company.configuration.manage",
        "company.memberships.manage",
        "company.reports.view",
        "company.roles.manage",
        "company.users.manage",
        "company.visibility.manage",
        "company.workspaces.manage",
    }

    for table in ("company_workspaces", "company_visibility_rules"):
        assert db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone()

    db.close()


def test_company_platform_routes_are_registered():
    from phoenix_core.http_api.company import router as company_router
    from phoenix_core.http_api.reports import router as reports_router
    from phoenix_core.http_api.workspaces import router as workspaces_router

    company_paths = {route.path for route in company_router.routes}
    assert "/api/v1/company/activity" in company_paths
    assert "/api/v1/company/users" in company_paths
    assert "/api/v1/company/roles" in company_paths

    assert {route.path for route in reports_router.routes} == {"/api/v1/company/reports"}
    assert {route.path for route in workspaces_router.routes} == {
        "/api/v1/company/workspaces",
        "/api/v1/company/workspaces/{module_code}",
    }
