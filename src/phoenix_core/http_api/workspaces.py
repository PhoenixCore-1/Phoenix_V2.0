"""Company Platform workspace configuration HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Request

from phoenix_core.audit.domain import AuditEvent
from phoenix_core.company.workspaces import CompanyWorkspaceService
from phoenix_core.http_api.authorization import resolve_request_context

router = APIRouter(prefix="/api/v1/company/workspaces", tags=["Company Platform"])


def _workspace_service(request: Request) -> CompanyWorkspaceService:
    core = request.app.state.core_api.core_service
    return CompanyWorkspaceService(core.db, core.module_service, core.entitlement_service)


@router.get("")
async def list_workspaces(request: Request):
    context = await resolve_request_context(request)
    items = _workspace_service(request).list(context.organisation_id)
    return {"data": {"items": items}, "request_id": context.request_id}


@router.patch("/{module_code}")
async def update_workspace(request: Request, module_code: str):
    context = await resolve_request_context(request)
    request.app.state.core_api.require_permission(context, "company.workspaces.manage")
    payload = await request.json()
    result = _workspace_service(request).update(
        context.organisation_id,
        module_code,
        display_name=payload.get("display_name"),
        visible=payload.get("visible"),
        sort_order=payload.get("sort_order"),
    )
    module = request.app.state.core_api.core_service.module_service.get_by_code(module_code)
    request.app.state.core_api.core_service.audit_service.record(
        AuditEvent.create(
            action="COMPANY_WORKSPACE_UPDATED",
            organisation_id=context.organisation_id,
            identity_id=context.identity_id,
            target_type="MODULE",
            target_id=UUID(str(module.id)),
            request_id=context.request_id,
        )
    )
    return {"data": result, "request_id": context.request_id}
