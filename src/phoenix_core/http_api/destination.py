"""HTTP transport for Phoenix platform destination resolution."""

from uuid import UUID

from fastapi import APIRouter, Request

from phoenix_core.errors import AuthenticationError, ValidationError
from phoenix_core.platform.destination import destination_payload

router = APIRouter(prefix="/api/v1/platform", tags=["platform"])
SESSION_COOKIE = "phoenix_session"
ORGANISATION_HEADER = "X-Phoenix-Organisation"


def _session_id(request: Request, core_api):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise AuthenticationError("Authentication required.")
    return core_api.resolve_session_id(token)


def _organisation_id(request: Request):
    value = request.headers.get(ORGANISATION_HEADER)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError as exc:
        raise ValidationError("Invalid organisation context.") from exc


@router.get("/destination")
def resolve_destination(request: Request):
    core_api = request.app.state.core_api
    context = core_api.resolve_context(
        request_id=request.state.request_id,
        session_id=_session_id(request, core_api),
        organisation_id=_organisation_id(request),
    )
    return {"data": destination_payload(context), "request_id": request.state.request_id}
