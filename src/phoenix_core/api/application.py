"""Framework-independent Phoenix Core API application boundary."""

from phoenix_core.api.context import RequestContextResolver
from phoenix_core.api.contracts import ApiResponse
from phoenix_core.auth.service import AuthenticationService
from phoenix_core.errors import AuthorizationError


class CoreApi:
    """Authoritative application-facing API boundary for Phoenix Core."""

    def __init__(self, db, core_service):
        self.db = db
        self.core_service = core_service
        self.authentication_service = AuthenticationService(db)
        self.context_resolver = RequestContextResolver(db, core_service)

    def resolve_context(
        self,
        *,
        request_id: str,
        session_id,
        organisation_id=None,
    ):
        return self.context_resolver.resolve(
            request_id=request_id,
            session_id=session_id,
            organisation_id=organisation_id,
        )

    @staticmethod
    def require_permission(context, permission: str) -> None:
        if not context.has_permission(permission):
            raise AuthorizationError("Permission denied.")

    @staticmethod
    def require_entitlement(context, module_code: str) -> None:
        if not context.has_entitlement(module_code):
            raise AuthorizationError("Module entitlement required.")

    def authenticate(
        self,
        *,
        request_id: str,
        username: str,
        password: str,
        organisation_id=None,
    ) -> ApiResponse:
        session, token = self.authentication_service.authenticate(
            username,
            password,
            organisation_id,
        )

        return ApiResponse(
            data={
                "session_id": str(session.id),
                "identity_id": str(session.identity_id),
                "token": token,
                "status": session.status,
                "expires_at": session.expires_at.isoformat(),
            },
            request_id=request_id,
        )

    def revoke_session(
        self,
        *,
        request_id: str,
        token: str,
    ) -> ApiResponse:
        revoked = self.core_service.revoke_session(token)

        return ApiResponse(
            data={
                "revoked": revoked,
            },
            request_id=request_id,
        )

    def get_current_identity(
        self,
        *,
        request_id: str,
        session_id,
        organisation_id=None,
    ) -> ApiResponse:
        context = self.resolve_context(
            request_id=request_id,
            session_id=session_id,
            organisation_id=organisation_id,
        )

        identity = self.core_service.get_identity(context.identity_id)

        return ApiResponse(
            data={
                "id": str(identity.id),
                "type": identity.identity_type,
                "status": identity.status,
            },
            request_id=context.request_id,
        )
    def get_current_organisation(
        self,
        *,
        request_id: str,
        session_id,
        organisation_id=None,
    ) -> ApiResponse:
        context = self.resolve_context(
            request_id=request_id,
            session_id=session_id,
            organisation_id=organisation_id,
        )

        organisation = self.core_service.get_organisation(
            context.organisation_id
        )

        return ApiResponse(
            data={
                "id": str(organisation.id),
                "code": organisation.code,
                "name": organisation.name,
                "status": organisation.status,
                "created_at": organisation.created_at.isoformat(),
            },
            request_id=context.request_id,
        )
    def get_current_user(
        self,
        *,
        request_id: str,
        session_id,
        organisation_id=None,
    ) -> ApiResponse:
        context = self.resolve_context(
            request_id=request_id,
            session_id=session_id,
            organisation_id=organisation_id,
        )

        user = self.core_service.get_user_by_identity(
            context.identity_id
        )

        return ApiResponse(
            data={
                "id": str(user.id),
                "identity_id": str(user.identity_id),
                "username": user.username,
                "display_name": user.display_name,
                "status": user.status,
                "created_at": user.created_at.isoformat(),
            },
            request_id=context.request_id,
        )
