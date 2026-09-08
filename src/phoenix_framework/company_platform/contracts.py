"""Contracts for the generic Phoenix Company Platform experience."""

from dataclasses import dataclass
from typing import Tuple

from phoenix_framework.contracts import NavigationItem


class CompanyPlatformCapabilities:
    """Stable capability identifiers owned by the Company Platform boundary."""

    COMPANY_ADMINISTRATION = "company.administration"
    USER_ADMINISTRATION = "company.users"
    ROLE_PERMISSION_ADMINISTRATION = "company.roles_permissions"
    DATA_VISIBILITY_ADMINISTRATION = "company.data_visibility"
    WORKSPACE_ADMINISTRATION = "company.workspaces"
    ACTIVITY_OVERVIEW = "company.activity"
    REPORTING = "company.reporting"
    AUDIT_VIEW = "company.audit"
    NOTIFICATIONS = "company.notifications"


@dataclass(frozen=True)
class CompanyPlatformContract:
    """Describes the tenant administration/oversight surface.

    Identity, tenancy, authorization, licensing, audit authority and business
    transactions remain owned by Phoenix Core or the relevant business module.
    """

    code: str = "company_platform"
    name: str = "Company Platform"
    version: str = "1.0.0"
    capabilities: Tuple[str, ...] = (
        CompanyPlatformCapabilities.COMPANY_ADMINISTRATION,
        CompanyPlatformCapabilities.USER_ADMINISTRATION,
        CompanyPlatformCapabilities.ROLE_PERMISSION_ADMINISTRATION,
        CompanyPlatformCapabilities.DATA_VISIBILITY_ADMINISTRATION,
        CompanyPlatformCapabilities.WORKSPACE_ADMINISTRATION,
        CompanyPlatformCapabilities.ACTIVITY_OVERVIEW,
        CompanyPlatformCapabilities.REPORTING,
        CompanyPlatformCapabilities.AUDIT_VIEW,
        CompanyPlatformCapabilities.NOTIFICATIONS,
    )


COMPANY_PLATFORM_NAVIGATION: Tuple[NavigationItem, ...] = (
    NavigationItem("company.dashboard", "Dashboard", "/company", icon="dashboard", order=10),
    NavigationItem("company.company", "Company", "/company/company", icon="building", order=20),
    NavigationItem("company.users", "Users", "/company/users", icon="users", order=30),
    NavigationItem("company.roles", "Roles & Permissions", "/company/roles", icon="shield", order=40),
    NavigationItem("company.visibility", "Data Visibility", "/company/data-visibility", icon="visibility", order=50),
    NavigationItem("company.workspaces", "Workspaces", "/company/workspaces", icon="layout", order=60),
    NavigationItem("company.activity", "Activity", "/company/activity", icon="activity", order=70),
    NavigationItem("company.reporting", "Reporting", "/company/reporting", icon="report", order=80),
    NavigationItem("company.audit", "Audit", "/company/audit", icon="audit", order=90),
    NavigationItem("company.notifications", "Notifications", "/company/notifications", icon="notifications", order=100),
)
