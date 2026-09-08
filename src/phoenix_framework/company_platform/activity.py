"""Company Platform activity overview boundary.

Activity is a tenant-scoped presentation projection. Authoritative events,
audit records and business activity remain owned by Phoenix Core or the
relevant business module.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class CompanyActivityItem:
    """Read-only activity item supplied by an authoritative source."""

    activity_id: UUID
    occurred_at: datetime
    category: str
    summary: str
    actor_identity_id: UUID | None
    source: str
    organisation_id: UUID

    @classmethod
    def from_core(cls, context: CompanyPlatformContext, *, activity_id: UUID, occurred_at: datetime, category: str, summary: str, actor_identity_id: UUID | None, source: str, organisation_id: UUID) -> "CompanyActivityItem":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Activity does not match request organisation")
        return cls(activity_id, occurred_at, category, summary, actor_identity_id, source, organisation_id)


@dataclass(frozen=True)
class CompanyActivityView:
    """Read-only tenant activity overview."""

    organisation_id: UUID
    items: Tuple[CompanyActivityItem, ...]


class CompanyActivityAdministrationService:
    """Framework orchestration boundary for company activity presentation."""

    @staticmethod
    def get_activity_item(context: CompanyPlatformContext, **activity: object) -> CompanyActivityItem:
        return CompanyActivityItem.from_core(context, **activity)

    @staticmethod
    def get_activity_view(context: CompanyPlatformContext, items: Tuple[CompanyActivityItem, ...]) -> CompanyActivityView:
        context.require_access()
        for item in items:
            if item.organisation_id != context.organisation_id:
                raise PermissionError("Activity does not match request organisation")
        return CompanyActivityView(context.organisation_id, tuple(items))
