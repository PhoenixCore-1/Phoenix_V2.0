"""Company Platform dashboard projection/orchestration boundary.

The dashboard is an administrative tenant overview. It consumes authoritative
Core-supplied company context and read-only summary data; it does not own
business transactions, licensing, or tenant persistence.
"""

from dataclasses import dataclass
from typing import Tuple
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.contracts import CompanyContext, ModuleDescriptor


@dataclass(frozen=True)
class CompanyDashboardSnapshot:
    """Read-only summary metrics supplied by authoritative platform services."""

    user_count: int = 0
    active_user_count: int = 0
    activity_count: int = 0
    visible_modules: Tuple[ModuleDescriptor, ...] = ()
    attention_items: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.user_count < 0 or self.active_user_count < 0 or self.activity_count < 0:
            raise ValueError("Dashboard counts cannot be negative")
        if self.active_user_count > self.user_count:
            raise ValueError("Active user count cannot exceed user count")


@dataclass(frozen=True)
class CompanyDashboardView:
    """Read-only tenant dashboard view for the current organisation."""

    organisation_id: UUID
    company_name: str
    company_active: bool
    user_count: int
    active_user_count: int
    activity_count: int
    visible_modules: Tuple[ModuleDescriptor, ...]
    attention_items: Tuple[str, ...]

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        company: CompanyContext,
        snapshot: CompanyDashboardSnapshot,
    ) -> "CompanyDashboardView":
        """Project authoritative Core/platform data into the Framework dashboard."""
        context.require_access()
        if company.organisation_id != context.organisation_id:
            raise PermissionError("Company context does not match request organisation")
        return cls(
            organisation_id=company.organisation_id,
            company_name=company.name,
            company_active=company.active,
            user_count=snapshot.user_count,
            active_user_count=snapshot.active_user_count,
            activity_count=snapshot.activity_count,
            visible_modules=tuple(snapshot.visible_modules),
            attention_items=tuple(snapshot.attention_items),
        )


class CompanyDashboardService:
    """Framework orchestration boundary for the Company Platform dashboard."""

    @staticmethod
    def get_dashboard_view(
        context: CompanyPlatformContext,
        company: CompanyContext,
        snapshot: CompanyDashboardSnapshot,
    ) -> CompanyDashboardView:
        return CompanyDashboardView.from_core(context, company, snapshot)
