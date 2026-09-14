"""Company Platform reporting endpoints backed by Phoenix Core authority."""

from fastapi import APIRouter, Request

from phoenix_core.http_api.authorization import resolve_request_context

router = APIRouter(prefix="/api/v1/company/reports", tags=["Company Platform"])


@router.get("")
async def company_reports(request: Request):
    """Return tenant-level administration and oversight metrics.

    This endpoint intentionally reports only company-platform concerns. It does
    not become an operational reporting authority for business modules.
    """
    context = await resolve_request_context(request)
    core = request.app.state.core_api
    core.require_permission(context, "company.reports.view")
    service = core.core_service

    memberships = service.list_memberships(context.organisation_id)
    roles = service.list_roles(context.organisation_id)
    permissions = service.list_permissions()

    active_users = sum(1 for item in memberships if item.status == "ACTIVE")
    suspended_users = sum(1 for item in memberships if item.status == "SUSPENDED")
    removed_users = sum(1 for item in memberships if item.status == "REMOVED")
    active_roles = sum(1 for item in roles if item.status == "ACTIVE")
    disabled_roles = sum(1 for item in roles if item.status == "DISABLED")

    return {
        "data": {
            "organisation_id": str(context.organisation_id),
            "people": {
                "total_memberships": len(memberships),
                "active": active_users,
                "suspended": suspended_users,
                "removed": removed_users,
            },
            "roles": {
                "total": len(roles),
                "active": active_roles,
                "disabled": disabled_roles,
            },
            "security": {
                "effective_permissions": len(context.permissions),
                "available_permissions": len(permissions),
            },
            "modules": {
                "entitled": sorted(context.entitlements),
            },
            "report_scope": "COMPANY_ADMINISTRATION",
        },
        "request_id": context.request_id,
    }
