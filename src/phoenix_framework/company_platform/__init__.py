"""Phoenix Company Platform V1.0 framework boundary."""

from phoenix_framework.company_platform.activity import CompanyActivityAdministrationService, CompanyActivityItem, CompanyActivityView
from phoenix_framework.company_platform.administration import CompanyAdministrationService, CompanyAdministrationView
from phoenix_framework.company_platform.audit import CompanyAuditItem, CompanyAuditService, CompanyAuditView
from phoenix_framework.company_platform.actions import (
    CompanyAdministrationAction,
    CompanyAdministrationExecutor,
    CompanyAdministrationRequest,
    CompanyAdministrationResult,
)
from phoenix_framework.company_platform.contracts import COMPANY_PLATFORM_NAVIGATION, CompanyPlatformCapabilities, CompanyPlatformContract
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.dashboard import CompanyDashboardService, CompanyDashboardSnapshot, CompanyDashboardView
from phoenix_framework.company_platform.notifications import CompanyNotificationItem, CompanyNotificationsService, CompanyNotificationsView
from phoenix_framework.company_platform.reporting import CompanyReportDefinitionView, CompanyReportResultView, CompanyReportingService, CompanyReportingView
from phoenix_framework.company_platform.roles import CompanyPermissionView, CompanyRoleView, CompanyRolesPermissionsService, CompanyRolesPermissionsView
from phoenix_framework.company_platform.users import CompanyUserAdministrationService, CompanyUserView, CompanyUsersView
from phoenix_framework.company_platform.visibility import DataVisibilityAdministrationService, DataVisibilityRuleView, DataVisibilityView
from phoenix_framework.company_platform.workspaces import CompanyWorkspaceAdministrationService, CompanyWorkspacesView, WorkspaceView

__all__ = [
    "COMPANY_PLATFORM_NAVIGATION", "CompanyActivityAdministrationService", "CompanyActivityItem", "CompanyActivityView",
    "CompanyAdministrationAction", "CompanyAdministrationExecutor", "CompanyAdministrationRequest", "CompanyAdministrationResult",
    "CompanyAdministrationService", "CompanyAdministrationView", "CompanyAuditItem", "CompanyAuditService", "CompanyAuditView",
    "CompanyDashboardService", "CompanyDashboardSnapshot", "CompanyDashboardView", "CompanyNotificationItem", "CompanyNotificationsService",
    "CompanyNotificationsView", "CompanyPermissionView", "CompanyPlatformCapabilities", "CompanyPlatformContract", "CompanyPlatformContext",
    "CompanyReportDefinitionView", "CompanyReportResultView", "CompanyReportingService", "CompanyReportingView", "CompanyRoleView",
    "CompanyRolesPermissionsService", "CompanyRolesPermissionsView", "CompanyUserAdministrationService", "CompanyUserView", "CompanyUsersView",
    "DataVisibilityAdministrationService", "DataVisibilityRuleView", "DataVisibilityView", "CompanyWorkspaceAdministrationService",
    "CompanyWorkspacesView", "WorkspaceView",
]
