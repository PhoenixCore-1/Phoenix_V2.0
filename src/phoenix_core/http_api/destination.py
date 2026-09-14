"""HTTP transport for Phoenix platform destination resolution."""

from fastapi import APIRouter, Request

from phoenix_core.http_api.app import ORGANISATION_HEADER, _organisation_id, _session_id
from phoenix_core.platform.destination import destination_payload

router = APIRouter(prefix="/api/v1/platform", tags=["platform"])


@router.get("/destination")
def resolve_destination(request: Request):
    core_api = request.app.state.core_api
    context = core_api.resolve_context(
        request_id=request.state.request_id,
        session_id=_session_id(request, core_api),
        organisation_id=_organisation_id(request),
    )
    return {"data": destination_payload(context), "request_id": request.state.request_id}
