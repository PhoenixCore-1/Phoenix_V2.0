"""FastAPI transport adapter for Phoenix Core.

The adapter owns HTTP concerns only. Business authority remains in CoreApi
and Core application services.
"""

from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

from phoenix_core.api.application import CoreApi
from phoenix_core.api.contracts import error_from_exception
from phoenix_core.errors import AuthenticationError, ValidationError
from phoenix_core.http_api.company import router as company_router
from phoenix_core.http_api.reports import router as reports_router
from phoenix_core.http_api.settings import router as settings_router
from phoenix_core.http_api.visibility import router as visibility_router
from phoenix_core.http_api.workspaces import router as workspace_router
from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.migration_runner import apply_all as apply_all_migrations
from phoenix_core.services import CoreFoundationService

SESSION_COOKIE = "phoenix_session"
ORGANISATION_HEADER = "X-Phoenix-Organisation"
REQUEST_ID_HEADER = "X-Request-ID"


def _request_id(request: Request) -> str:
    return request.headers.get(REQUEST_ID_HEADER) or str(uuid4())


def _session_id(request: Request, core_api: CoreApi) -> UUID:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        raise AuthenticationError("Authentication required.")
    return core_api.resolve_session_id(token)


def _organisation_id(request: Request) -> UUID | None:
    value = request.headers.get(ORGANISATION_HEADER)
    if not value:
        return None
    try:
        return UUID(value)
    except ValueError as exc:
        raise ValidationError("Invalid organisation context.") from exc


def create_app(core_api: CoreApi) -> FastAPI:
    """Create the Phoenix Core HTTP API around an existing CoreApi."""
    application = FastAPI(title="Phoenix Core API", version="1.0")
    application.state.core_api = core_api
    application.include_router(company_router)
    application.include_router(workspace_router)
    application.include_router(visibility_router)
    application.include_router(reports_router)
    application.include_router(settings_router)

    @application.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request.state.request_id = _request_id(request)
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request.state.request_id
        return response

    @application.exception_handler(Exception)
    async def exception_handler(request: Request, exc: Exception):
        api_error = error_from_exception(exc, request_id=getattr(request.state, "request_id", _request_id(request)))
        status_code = {"VALIDATION_ERROR": 422, "NOT_FOUND": 404, "CONFLICT": 409, "AUTHENTICATION_ERROR": 401, "AUTHORIZATION_ERROR": 403, "CORE_ERROR": 500, "INTERNAL_ERROR": 500}.get(api_error.code, 500)
        return JSONResponse(status_code=status_code, content={"code": api_error.code, "message": api_error.message, "request_id": api_error.request_id})

    @application.get("/api/v1/health")
    def health(request: Request):
        return {"data": {"status": "ok", "service": "phoenix-core"}, "request_id": request.state.request_id}

    @application.post("/api/v1/auth/login")
    async def login(request: Request, response: Response):
        payload = await request.json()
        try:
            organisation_id = UUID(payload["organisation_id"]) if payload.get("organisation_id") else None
        except ValueError as exc:
            raise ValidationError("Invalid organisation_id.") from exc
        result = core_api.authenticate(request_id=request.state.request_id, username=str(payload.get("username", "")), password=str(payload.get("password", "")), organisation_id=organisation_id)
        response.set_cookie(SESSION_COOKIE, result.data["token"], httponly=True, secure=True, samesite="lax", path="/")
        data = dict(result.data)
        data.pop("token", None)
        return {"data": data, "request_id": result.request_id}

    @application.get("/api/v1/auth/session")
    def session(request: Request):
        session_id = _session_id(request, core_api)
        context = core_api.resolve_context(request_id=request.state.request_id, session_id=session_id, organisation_id=_organisation_id(request))
        return {"data": {"authenticated": True, "session_id": str(context.session_id), "identity_id": str(context.identity_id), "organisation_id": str(context.organisation_id), "permissions": sorted(context.permissions), "entitlements": sorted(context.entitlements)}, "request_id": request.state.request_id}

    @application.post("/api/v1/auth/logout")
    def logout(request: Request, response: Response):
        token = request.cookies.get(SESSION_COOKIE)
        if not token:
            response.delete_cookie(SESSION_COOKIE, path="/")
            return {"data": {"revoked": False}, "request_id": request.state.request_id}
        result = core_api.revoke_session(request_id=request.state.request_id, token=token)
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"data": result.data, "request_id": result.request_id}

    @application.get("/api/v1/me")
    def current_user(request: Request):
        result = core_api.get_current_user(request_id=request.state.request_id, session_id=_session_id(request, core_api), organisation_id=_organisation_id(request))
        return {"data": result.data, "request_id": result.request_id}

    @application.get("/api/v1/me/identity")
    def current_identity(request: Request):
        result = core_api.get_current_identity(request_id=request.state.request_id, session_id=_session_id(request, core_api), organisation_id=_organisation_id(request))
        return {"data": result.data, "request_id": result.request_id}

    @application.get("/api/v1/me/organisation")
    def current_organisation(request: Request):
        result = core_api.get_current_organisation(request_id=request.state.request_id, session_id=_session_id(request, core_api), organisation_id=_organisation_id(request))
        return {"data": result.data, "request_id": result.request_id}

    @application.get("/api/v1/me/permissions")
    def current_permissions(request: Request):
        context = core_api.resolve_context(request_id=request.state.request_id, session_id=_session_id(request, core_api), organisation_id=_organisation_id(request))
        return {"data": {"permissions": sorted(context.permissions)}, "request_id": request.state.request_id}

    @application.get("/api/v1/me/entitlements")
    def current_entitlements(request: Request):
        context = core_api.resolve_context(request_id=request.state.request_id, session_id=_session_id(request, core_api), organisation_id=_organisation_id(request))
        return {"data": {"entitlements": sorted(context.entitlements)}, "request_id": request.state.request_id}

    return application


def create_development_app(database_path: str = "phoenix_core.db") -> FastAPI:
    """Create a development API using all checked-in Core migrations."""
    db = SQLiteDatabase(database_path)
    apply_all_migrations(db)
    core_service = CoreFoundationService(db)
    api = CoreApi(db, core_service)
    return create_app(api)
