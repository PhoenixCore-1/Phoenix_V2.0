"""Controlled Company Platform company-configuration administration boundary.

The Framework represents tenant-level configuration requests and delegates
persistence and enforcement to authoritative Core/application services. It
must not become a second configuration store or security authority.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyConfigurationAction(str, Enum):
    """Supported tenant-level configuration operations."""

    SET_COMPANY_DEFAULT = "set_company_default"
    UPDATE_COMPANY_PREFERENCE = "update_company_preference"
    RESET_COMPANY_PREFERENCE = "reset_company_preference"
    ENABLE_PRESENTATION_FEATURE = "enable_presentation_feature"
    DISABLE_PRESENTATION_FEATURE = "disable_presentation_feature"
    SET_COMPANY_LOCALE = "set_company_locale"
    SET_COMPANY_TIMEZONE = "set_company_timezone"
    SET_COMPANY_DATE_FORMAT = "set_company_date_format"
    SET_COMPANY_CURRENCY_FORMAT = "set_company_currency_format"


@dataclass(frozen=True)
class CompanyConfigurationAdministrationRequest:
    """Immutable tenant-bound company configuration operation."""

    action: CompanyConfigurationAction
    organisation_id: UUID
    key: str | None = None
    value: str | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyConfigurationAction,
        key: str | None = None,
        value: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyConfigurationAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            key=key,
            value=value,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Configuration request does not match request organisation")

        if self.action in {
            CompanyConfigurationAction.SET_COMPANY_DEFAULT,
            CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE,
            CompanyConfigurationAction.RESET_COMPANY_PREFERENCE,
        } and not self.key:
            raise ValueError("Company configuration operation requires a key")

        if self.action in {
            CompanyConfigurationAction.SET_COMPANY_DEFAULT,
            CompanyConfigurationAction.UPDATE_COMPANY_PREFERENCE,
        } and self.value is None:
            raise ValueError("Company configuration operation requires a value")

        if self.action in {
            CompanyConfigurationAction.ENABLE_PRESENTATION_FEATURE,
            CompanyConfigurationAction.DISABLE_PRESENTATION_FEATURE,
        } and not self.key:
            raise ValueError("Presentation feature operation requires a feature key")

        format_actions = {
            CompanyConfigurationAction.SET_COMPANY_LOCALE,
            CompanyConfigurationAction.SET_COMPANY_TIMEZONE,
            CompanyConfigurationAction.SET_COMPANY_DATE_FORMAT,
            CompanyConfigurationAction.SET_COMPANY_CURRENCY_FORMAT,
        }
        if self.action in format_actions and self.value is None:
            raise ValueError("Company format configuration requires a value")


@dataclass(frozen=True)
class CompanyConfigurationAdministrationResult:
    """Immutable result returned by the authoritative configuration executor."""

    action: CompanyConfigurationAction
    organisation_id: UUID
    key: str | None
    success: bool
    message: str = ""


class CompanyConfigurationAdministrationExecutor(Protocol):
    """Authoritative Core/application boundary for configuration operations."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyConfigurationAdministrationRequest,
    ) -> CompanyConfigurationAdministrationResult: ...


class CompanyConfigurationAdministrationService:
    """Framework facade; validates and delegates company configuration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyConfigurationAction,
        key: str | None = None,
        value: str | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyConfigurationAdministrationRequest:
        return CompanyConfigurationAdministrationRequest.create(
            context,
            action=action,
            key=key,
            value=value,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyConfigurationAdministrationRequest,
        executor: CompanyConfigurationAdministrationExecutor,
    ) -> CompanyConfigurationAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
