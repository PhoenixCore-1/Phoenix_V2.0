"""Application boundary for tenant-scoped Company Platform visibility."""

from uuid import UUID

from phoenix_core.audit.domain import AuditEvent
from phoenix_core.company.visibility import CompanyVisibilityService


class CompanyVisibilityApplicationService:
    """Own Company visibility authorization, persistence, and audit orchestration."""

    PERMISSION = "company.visibility.manage"

    def __init__(self, core_api):
        self.core_api = core_api
        self.service = CompanyVisibilityService(core_api.db)

    def list(self, context):
        self.core_api.require_permission(context, self.PERMISSION)
        return self.service.list(context.organisation_id)

    def upsert(
        self,
        context,
        *,
        scope_type: str,
        resource_code: str,
        visible: bool | None,
        membership_id: UUID | None = None,
        role_id: UUID | None = None,
    ):
        self.core_api.require_permission(context, self.PERMISSION)
        result = self.service.upsert(
            context.organisation_id,
            scope_type=scope_type,
            resource_code=resource_code,
            visible=visible,
            membership_id=membership_id,
            role_id=role_id,
        )
        self._audit(
            context,
            action="COMPANY_VISIBILITY_UPDATED",
            target_id=UUID(result["id"]),
        )
        return result

    def delete(self, context, rule_id: UUID):
        self.core_api.require_permission(context, self.PERMISSION)
        removed = self.service.delete(context.organisation_id, rule_id)
        self._audit(
            context,
            action="COMPANY_VISIBILITY_DELETED",
            target_id=rule_id,
        )
        return removed

    def _audit(self, context, *, action: str, target_id: UUID) -> None:
        self.core_api.core_service.audit_service.record(AuditEvent.create(
            action=action,
            organisation_id=context.organisation_id,
            identity_id=context.identity_id,
            target_type="VISIBILITY_RULE",
            target_id=target_id,
            request_id=context.request_id,
        ))
