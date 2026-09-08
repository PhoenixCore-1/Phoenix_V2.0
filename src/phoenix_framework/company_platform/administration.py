"""Company Administration presentation/orchestration boundary.

The Company Platform never becomes the authority for tenant data.  Company
state is supplied by Phoenix Core and projected into this Framework surface.
"""

from dataclasses import dataclass
from uuid import UUID

from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.contracts import CompanyContext


@dataclass(frozen=True)
class CompanyAdministrationView:
    """Read-only Company Administration view for the current tenant."""

    organisation_id: UUID
    name: str
    active: bool

    @classmethod
    def from_core(
        cls,
        context: CompanyPlatformContext,
        company: CompanyContext,
    ) -> "CompanyAdministrationView":
        """Project authoritative Core company state into the Framework UI."""
        context.require_access()
        if company.organisation_id != context.organisation_id:
            raise PermissionError("Company context does not match request organisation")
        return cls(
            organisation_id=company.organisation_id,
            name=company.name,
            active=company.active,
        )


class CompanyAdministrationService:
    """Framework orchestration boundary for Company Administration."""

    @staticmethod
    def get_company_view(
        context: CompanyPlatformContext,
        company: CompanyContext,
    ) -> CompanyAdministrationView:
        return CompanyAdministrationView.from_core(context, company)
