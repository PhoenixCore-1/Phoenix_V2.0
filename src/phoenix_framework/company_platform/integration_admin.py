"""Controlled Company Platform integration administration boundary.

The Framework represents tenant-level integration configuration and action
requests. Credentials, connection security, persistence and execution remain
authoritative Core/application concerns.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyIntegrationAction(str, Enum):
    """Supported tenant integration administration operations."""

    ENABLE_INTEGRATION = "enable_integration"
    DISABLE_INTEGRATION = "disable_integration"
    UPDATE_INTEGRATION_CONFIGURATION = "update_integration_configuration"
    TEST_CONNECTION = "test_connection"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    REFRESH_CONNECTION = "refresh_connection"
    ROTATE_CREDENTIALS = "rotate_credentials"


@dataclass(frozen=True)
class CompanyIntegrationAdministrationRequest:
    """Immutable tenant-bound integration operation."""

    action: CompanyIntegrationAction
    organisation_id: UUID
    integration_key: str
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyIntegrationAction,
        integration_key: str,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyIntegrationAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            integration_key=integration_key,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Integration request does not match request organisation")
        if not self.integration_key.strip():
            raise ValueError("Integration operation requires an integration key")

        configuration_actions = {
            CompanyIntegrationAction.UPDATE_INTEGRATION_CONFIGURATION,
            CompanyIntegrationAction.CONNECT,
        }
        if self.action in configuration_actions and not self.parameters:
            raise ValueError("This integration operation requires configuration parameters")


@dataclass(frozen=True)
class CompanyIntegrationAdministrationResult:
    """Immutable result returned by the authoritative integration executor."""

    action: CompanyIntegrationAction
    organisation_id: UUID
    integration_key: str
    success: bool
    message: str = ""


class CompanyIntegrationAdministrationExecutor(Protocol):
    """Authoritative Core/integration application boundary."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyIntegrationAdministrationRequest,
    ) -> CompanyIntegrationAdministrationResult: ...


class CompanyIntegrationAdministrationService:
    """Framework facade; validates and delegates integration administration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyIntegrationAction,
        integration_key: str,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyIntegrationAdministrationRequest:
        return CompanyIntegrationAdministrationRequest.create(
            context,
            action=action,
            integration_key=integration_key,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyIntegrationAdministrationRequest,
        executor: CompanyIntegrationAdministrationExecutor,
    ) -> CompanyIntegrationAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
