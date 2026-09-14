"""Company Platform data visibility HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Request
from pydantic import BaseModel

from phoenix_core.company.visibility_application import CompanyVisibilityApplicationService
from phoenix_core.http_api.authorization import resolve_request_context

router = APIRouter(prefix="/api/v1/company/visibility", tags=["Company Platform"])


def _application(request: Request) -> CompanyVisibilityApplicationService:
    return CompanyVisibilityApplicationService(request.app.state.core_api)


class VisibilityPayload(BaseModel):
    scope_type: str = ""
    resource_code: str = ""
    visible: bool | None = None
    membership_id: UUID | None = None
    role_id: UUID | None = None


@router.get("")
async def list_visibility(request: Request):
    context = await resolve_request_context(request)
    return {"data": {"items": _application(request).list(context)}, "request_id": context.request_id}


@router.put("")
async def set_visibility(request: Request, payload: VisibilityPayload):
    context = await resolve_request_context(request)
    result = _application(request).upsert(
        context,
        scope_type=payload.scope_type,
        resource_code=payload.resource_code,
        visible=payload.visible,
        membership_id=payload.membership_id,
        role_id=payload.role_id,
    )
    return {"data": result, "request_id": context.request_id}


@router.delete("/{rule_id}")
async def delete_visibility(request: Request, rule_id: UUID):
    context = await resolve_request_context(request)
    removed = _application(request).delete(context, rule_id)
    return {"data": {"removed": removed, "id": str(rule_id)}, "request_id": context.request_id}
