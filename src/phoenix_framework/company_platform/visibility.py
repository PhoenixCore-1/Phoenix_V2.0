"""Company Platform data-visibility administration boundary.

Visibility policy definitions are presented here for tenant administration, but
actual authorization and enforcement remain with Phoenix Core and the relevant
business-domain services.
"""

from dataclasses import dataclass
from typing import FrozenSet, Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext


@dataclass(frozen=True)
class DataVisibilityRuleView:
    """Read-only representation of a tenant visibility rule."""

    rule_id: UUID
    name: str
    resource: str
    scope: str
    allowed_roles: FrozenSet[str]
    enabled: bool
    organisation_id: UUID

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        *,
        rule_id: UUID,
        name: str,
        resource: str,
        scope: str,
        allowed_roles: FrozenSet[str],
        enabled: bool,
        organisation_id: UUID,
    ) -> "DataVisibilityRuleView":
        context.require_access()
        if organisation_id != context.organisation_id:
            raise PermissionError("Visibility rule does not match request organisation")
        return cls(
            rule_id=rule_id,
            name=name,
            resource=resource,
            scope=scope,
            allowed_roles=frozenset(allowed_roles),
            enabled=enabled,
            organisation_id=organisation_id,
        )


@dataclass(frozen=True)
class DataVisibilityView:
    """Read-only tenant-scoped visibility administration view."""

    organisation_id: UUID
    rules: Tuple[DataVisibilityRuleView, ...]


class DataVisibilityAdministrationService:
    """Framework orchestration boundary for data visibility administration."""

    @staticmethod
    def get_rule_view(
        context: CompanyPlatformContext,
        **rule: object,
    ) -> DataVisibilityRuleView:
        return DataVisibilityRuleView.from_core(context, **rule)

    @staticmethod
    def get_visibility_view(
        context: CompanyPlatformContext,
        rules: Tuple[DataVisibilityRuleView, ...],
    ) -> DataVisibilityView:
        context.require_access()
        for rule in rules:
            if rule.organisation_id != context.organisation_id:
                raise PermissionError("Visibility rule does not match request organisation")
        return DataVisibilityView(context.organisation_id, tuple(rules))
