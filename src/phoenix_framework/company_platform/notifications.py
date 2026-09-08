"""Company Platform notification presentation boundary.

Notifications are consumed as authoritative, tenant-scoped projections. This
Framework layer does not own notification generation, delivery or persistence.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class CompanyNotificationItem:
    """Immutable notification projection supplied by an authoritative source."""

    notification_id: UUID
    created_at: datetime
    title: str
    message: str
    category: str
    severity: str
    recipient_identity_id: UUID
    read: bool
    source: str
    organisation_id: UUID
    action_route: str | None = None

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        notification_id: UUID,
        created_at: datetime,
        title: str,
        message: str,
        category: str,
        severity: str,
        recipient_identity_id: UUID,
        read: bool,
        source: str,
        organisation_id: UUID,
        action_route: str | None = None,
    ) -> "CompanyNotificationItem":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Notification does not match request organisation")
        return cls(
            notification_id,
            created_at,
            title,
            message,
            category,
            severity,
            recipient_identity_id,
            read,
            source,
            organisation_id,
            action_route,
        )


@dataclass(frozen=True)
class CompanyNotificationsView:
    """Tenant-scoped immutable notification centre projection."""

    organisation_id: UUID
    items: Tuple[CompanyNotificationItem, ...]

    @property
    def unread_count(self) -> int:
        return sum(1 for item in self.items if not item.read)


class CompanyNotificationsService:
    """Framework orchestration boundary for notification presentation."""

    @staticmethod
    def get_notification_item(
        context: CompanyPlatformContext,
        **notification: object,
    ) -> CompanyNotificationItem:
        return CompanyNotificationItem.from_core(context, **notification)

    @staticmethod
    def get_notifications_view(
        context: CompanyPlatformContext,
        items: Tuple[CompanyNotificationItem, ...],
    ) -> CompanyNotificationsView:
        context.require_access()
        for item in items:
            if item.organisation_id != context.organisation_id:
                raise PermissionError("Notification does not match request organisation")
        return CompanyNotificationsView(context.organisation_id, tuple(items))
