"""Company Platform HTTP read endpoints backed by Phoenix Core authority."""

from fastapi import APIRouter, Request

from phoenix_core.http_api.authorization import resolve_request_context


router = APIRouter(prefix="/api/v1/company", tags=["Company Platform"])


def _organisation(context):
    return context.organisation_id


@router.get("")
async def current_company(request: Request):
    context = await resolve_request_context(request)
    organisation = request.app.state.core_api.core_service.get_organisation(_organisation(context))
    return {
        "data": {
            "id": str(organisation.id),
            "code": organisation.code,
            "name": organisation.name,
            "status": organisation.status,
            "created_at": organisation.created_at.isoformat(),
        },
        "request_id": context.request_id,
    }


@router.get("/users")
async def users(request: Request):
    context = await resolve_request_context(request)
    service = request.app.state.core_api.core_service
    memberships = service.list_memberships(_organisation(context))
    items = []
    for membership in memberships:
        user = service.get_user_by_identity(membership.identity_id)
        items.append(
            {
                "id": str(user.id),
                "identity_id": str(user.identity_id),
                "username": user.username,
                "display_name": user.display_name,
                "user_status": user.status,
                "membership_id": str(membership.id),
                "membership_status": membership.status,
                "created_at": user.created_at.isoformat(),
            }
        )
    return {"data": {"items": items}, "request_id": context.request_id}


@router.get("/memberships")
async def memberships(request: Request):
    context = await resolve_request_context(request)
    items = request.app.state.core_api.core_service.list_memberships(_organisation(context))
    return {
        "data": {
            "items": [
                {
                    "id": str(item.id),
                    "identity_id": str(item.identity_id),
                    "organisation_id": str(item.organisation_id),
                    "status": item.status,
                    "created_at": item.created_at.isoformat(),
                }
                for item in items
            ]
        },
        "request_id": context.request_id,
    }


@router.get("/roles")
async def roles(request: Request):
    context = await resolve_request_context(request)
    items = request.app.state.core_api.core_service.list_roles(_organisation(context))
    return {
        "data": {
            "items": [
                {
                    "id": str(item.id),
                    "organisation_id": str(item.organisation_id),
                    "code": item.code,
                    "name": item.name,
                    "scope": item.scope,
                    "status": item.status,
                    "created_at": item.created_at.isoformat(),
                }
                for item in items
            ]
        },
        "request_id": context.request_id,
    }


@router.get("/permissions")
async def permissions(request: Request):
    context = await resolve_request_context(request)
    items = request.app.state.core_api.core_service.list_permissions()
    return {
        "data": {
            "items": [
                {"id": str(item.id), "code": item.code, "name": item.name, "created_at": item.created_at.isoformat()}
                for item in items
            ]
        },
        "request_id": context.request_id,
    }
