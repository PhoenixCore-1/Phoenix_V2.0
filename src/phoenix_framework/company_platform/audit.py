"""Company Platform audit presentation boundary.

Audit records remain authoritative in Phoenix Core. This Framework layer only
projects authorised, tenant-scoped audit information for presentation.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class CompanyAuditItem:
    """Immutable audit record projection supplied by Phoenix Core."""

    audit_id: UUID
    occurred_at: datetime
    action: str
    resource: str
    resource_id: str | None
    actor_identity_id: UUID | None
    outcome: str
    organisation_id: UUID

    @classmethod
    def from_core(cls, context: CompanyPlatformContext, *, audit_id: UUID, occurred_at: datetime, action: str, resource: str, resource_id: str | None, actor_identity_id: UUID | None, outcome: str, organisation_id: UUID) -> "CompanyAuditItem":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Audit record does not match request organisation")
        return cls(audit_id, occurred_at, action, resource, resource_id, actor_identity_id, outcome, organisation_id)


@dataclass(frozen=True)
class CompanyAuditView:
    """Tenant-scoped immutable audit presentation."""

    organisation_id: UUID
    items: Tuple[CompanyAuditItem, ...]


class CompanyAuditService:
    """Framework orchestration boundary for audit presentation."""

    @staticmethod
    def get_audit_item(context: CompanyPlatformContext, **audit: object) -> CompanyAuditItem:
        return CompanyAuditItem.from_core(context, **audit)

    @staticmethod
    def get_audit_view(context: CompanyPlatformContext, items: Tuple[CompanyAuditItem, ...]) -> CompanyAuditView:
        context.require_access()
        for item in items:
            if item.organisation_id != context.organisation_id:
                raise PermissionError("Audit record does not match request organisation")
        return CompanyAuditView(context.organisation_id, tuple(items))
