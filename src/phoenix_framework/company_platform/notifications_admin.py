"""Controlled Company Platform notification administration boundary.

The Framework creates immutable tenant-bound notification administration
requests and delegates authoritative configuration and delivery operations to
Core notification services. It does not persist notifications or implement a
delivery engine.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Protocol
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


class CompanyNotificationAction(str, Enum):
    """Supported Company Platform notification administration operations."""

    UPDATE_COMPANY_PREFERENCES = "update_company_preferences"
    UPDATE_USER_PREFERENCES = "update_user_preferences"
    ENABLE_CHANNEL = "enable_channel"
    DISABLE_CHANNEL = "disable_channel"
    ENABLE_NOTIFICATION_TYPE = "enable_notification_type"
    DISABLE_NOTIFICATION_TYPE = "disable_notification_type"
    SEND_NOTIFICATION = "send_notification"
    MARK_READ = "mark_read"
    MARK_UNREAD = "mark_unread"
    DISMISS_NOTIFICATION = "dismiss_notification"


@dataclass(frozen=True)
class CompanyNotificationAdministrationRequest:
    """Immutable tenant-bound notification operation."""

    action: CompanyNotificationAction
    organisation_id: UUID
    identity_id: UUID | None = None
    notification_id: UUID | None = None
    parameters: tuple[tuple[str, str], ...] = ()

    @classmethod
    def create(
        cls,
        context: CompanyPlatformContext,
        *,
        action: CompanyNotificationAction,
        identity_id: UUID | None = None,
        notification_id: UUID | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> "CompanyNotificationAdministrationRequest":
        context.require_access()
        return cls(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=identity_id,
            notification_id=notification_id,
            parameters=tuple(sorted((parameters or {}).items())),
        )

    def validate_for(self, context: CompanyPlatformContext) -> None:
        context.require_access()
        if self.organisation_id != context.organisation_id:
            raise PermissionError("Notification administration request does not match request organisation")

        user_actions = {
            CompanyNotificationAction.UPDATE_USER_PREFERENCES,
            CompanyNotificationAction.MARK_READ,
            CompanyNotificationAction.MARK_UNREAD,
            CompanyNotificationAction.DISMISS_NOTIFICATION,
        }
        notification_actions = {
            CompanyNotificationAction.MARK_READ,
            CompanyNotificationAction.MARK_UNREAD,
            CompanyNotificationAction.DISMISS_NOTIFICATION,
        }
        preference_actions = {
            CompanyNotificationAction.UPDATE_COMPANY_PREFERENCES,
            CompanyNotificationAction.UPDATE_USER_PREFERENCES,
            CompanyNotificationAction.ENABLE_CHANNEL,
            CompanyNotificationAction.DISABLE_CHANNEL,
            CompanyNotificationAction.ENABLE_NOTIFICATION_TYPE,
            CompanyNotificationAction.DISABLE_NOTIFICATION_TYPE,
        }

        if self.action in user_actions and self.identity_id is None:
            raise ValueError("This notification operation requires an identity_id")
        if self.action in notification_actions and self.notification_id is None:
            raise ValueError("This notification operation requires a notification_id")
        if self.action == CompanyNotificationAction.UPDATE_COMPANY_PREFERENCES and not self.parameters:
            raise ValueError("Company notification preferences require parameters")
        if self.action == CompanyNotificationAction.UPDATE_USER_PREFERENCES and not self.parameters:
            raise ValueError("User notification preferences require parameters")
        if self.action in {
            CompanyNotificationAction.ENABLE_CHANNEL,
            CompanyNotificationAction.DISABLE_CHANNEL,
        } and "channel" not in {key for key, _ in self.parameters}:
            raise ValueError("Channel notification operations require a channel parameter")
        if self.action in {
            CompanyNotificationAction.ENABLE_NOTIFICATION_TYPE,
            CompanyNotificationAction.DISABLE_NOTIFICATION_TYPE,
        } and "notification_type" not in {key for key, _ in self.parameters}:
            raise ValueError("Notification type operations require a notification_type parameter")
        if self.action == CompanyNotificationAction.SEND_NOTIFICATION:
            if not self.identity_id:
                raise ValueError("Sending a notification requires an identity_id")
            if not self.parameters:
                raise ValueError("Sending a notification requires notification parameters")


@dataclass(frozen=True)
class CompanyNotificationAdministrationResult:
    """Immutable result envelope returned by the authoritative executor."""

    action: CompanyNotificationAction
    organisation_id: UUID
    identity_id: UUID | None
    notification_id: UUID | None
    success: bool
    message: str = ""


class CompanyNotificationAdministrationExecutor(Protocol):
    """Authoritative Core notification application boundary."""

    def execute(
        self,
        context: CompanyPlatformContext,
        request: CompanyNotificationAdministrationRequest,
    ) -> CompanyNotificationAdministrationResult: ...


class CompanyNotificationAdministrationService:
    """Framework facade; validates and delegates notification administration."""

    @staticmethod
    def build_request(
        context: CompanyPlatformContext,
        *,
        action: CompanyNotificationAction,
        identity_id: UUID | None = None,
        notification_id: UUID | None = None,
        parameters: Mapping[str, str] | None = None,
    ) -> CompanyNotificationAdministrationRequest:
        return CompanyNotificationAdministrationRequest.create(
            context,
            action=action,
            identity_id=identity_id,
            notification_id=notification_id,
            parameters=parameters,
        )

    @staticmethod
    def execute(
        context: CompanyPlatformContext,
        request: CompanyNotificationAdministrationRequest,
        executor: CompanyNotificationAdministrationExecutor,
    ) -> CompanyNotificationAdministrationResult:
        request.validate_for(context)
        return executor.execute(context, request)
