"""Company Platform role and permission administration boundary."""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyRoleAction(str, Enum):
    CREATE_ROLE = "create_role"
    UPDATE_ROLE = "update_role"
    DEACTIVATE_ROLE = "deactivate_role"
    ACTIVATE_ROLE = "activate_role"
    GRANT_PERMISSION = "grant_permission"
    REVOKE_PERMISSION = "revoke_permission"


@dataclass(frozen=True)
class CompanyRoleAdministrationRequest:
    """Immutable tenant-bound role/permission operation."""

    action: CompanyRoleAction
    organisation_id: UUID
    role_id: UUID | None = None
    permission_code: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(cls, context: CompanyPlatformContext, *, action: CompanyRoleAction, role_id: UUID | None = None, permission_code: str | None = None, parameters: Mapping[str, str] | None = None) -> "CompanyRoleAdministrationRequest":
        context.require_access()
        return cls(action, context.organisation_id, role_id, permission_code, tuple(sorted((parameters or {}).items())))

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Role administration request does not match request organisation")
        if self.action in {CompanyRoleAction.UPDATE_ROLE, CompanyRoleAction.DEACTIVATE_ROLE, CompanyRoleAction.ACTIVATE_ROLE, CompanyRoleAction.GRANT_PERMISSION, CompanyRoleAction.REVOKE_PERMISSION} and self.role_id is None:
            raise ValueError("This role operation requires a role_id")
        if self.action in {CompanyRoleAction.GRANT_PERMISSION, CompanyRoleAction.REVOKE_PERMISSION} and not self.permission_code:
            raise ValueError("Permission operations require a permission_code")


class CompanyRoleAdministrationExecutor(Protocol):
    """Authoritative Core application boundary for role administration."""

    def execute(self, context: CompanyPlatformContext, request: CompanyRoleAdministrationRequest): ...


class CompanyRoleAdministrationService:
    """Framework facade; role and permission mutations remain Core-owned."""

    @staticmethod
    def build_request(context: CompanyPlatformContext, *, action: CompanyRoleAction, role_id: UUID | None = None, permission_code: str | None = None, parameters: Mapping[str, str] | None = None) -> CompanyRoleAdministrationRequest:
        return CompanyRoleAdministrationRequest.create(context, action=action, role_id=role_id, permission_code=permission_code, parameters=parameters)

    @staticmethod
    def execute(context: CompanyPlatformContext, request: CompanyRoleAdministrationRequest, executor: CompanyRoleAdministrationExecutor):
        request.validate_for(context)
        return executor.execute(context, request)
