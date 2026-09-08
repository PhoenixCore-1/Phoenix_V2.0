"""Phoenix Company Platform V1.0 framework boundary."""

from phoenix_framework.company_platform.access import CompanyAccessService, CompanyCapabilityAccess
from phoenix_framework.company_platform.activity import CompanyActivityAdministrationService, CompanyActivityItem, CompanyActivityView
from phoenix_framework.company_platform.administration import CompanyAdministrationService, CompanyAdministrationView
from phoenix_framework.company_platform.audit import CompanyAuditItem, CompanyAuditService, CompanyAuditView
from phoenix_framework.company_platform.actions import CompanyAdministrationAction, CompanyAdministrationExecutor, CompanyAdministrationRequest, CompanyAdministrationResult, CompanyUserAction, CompanyUserAdministrationExecutor, CompanyUserAdministrationOperationService, CompanyUserAdministrationRequest
from phoenix_framework.company_platform.contracts import COMPANY_PLATFORM_NAVIGATION, CompanyPlatformCapabilities, CompanyPlatformContract
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.dashboard import CompanyDashboardService, CompanyDashboardSnapshot, CompanyDashboardView
from phoenix_framework.company_platform.navigation import CompanyNavigationService, CompanyNavigationView
from phoenix_framework.company_platform.notifications import CompanyNotificationItem, CompanyNotificationsService, CompanyNotificationsView
from phoenix_framework.company_platform.reporting import CompanyReportDefinitionView, CompanyReportResultView, CompanyReportingService, CompanyReportingView
from phoenix_framework.company_platform.roles import CompanyPermissionView, CompanyRoleView, CompanyRolesPermissionsService, CompanyRolesPermissionsView
from phoenix_framework.company_platform.roles_admin import CompanyRoleAction, CompanyRoleAdministrationExecutor, CompanyRoleAdministrationRequest, CompanyRoleAdministrationService
from phoenix_framework.company_platform.users import CompanyUserAdministrationService, CompanyUserView, CompanyUsersView
from phoenix_framework.company_platform.visibility import DataVisibilityAdministrationService, DataVisibilityRuleView, DataVisibilityView
from phoenix_framework.company_platform.visibility_admin import CompanyVisibilityAction, CompanyVisibilityAdministrationExecutor, CompanyVisibilityAdministrationRequest, CompanyVisibilityAdministrationResult, CompanyVisibilityAdministrationService
from phoenix_framework.company_platform.workspaces import CompanyWorkspaceAdministrationService, CompanyWorkspacesView, WorkspaceView

__all__ = [
    "COMPANY_PLATFORM_NAVIGATION", "CompanyAccessService", "CompanyActivityAdministrationService", "CompanyActivityItem", "CompanyActivityView",
    "CompanyAdministrationAction", "CompanyAdministrationExecutor", "CompanyAdministrationRequest", "CompanyAdministrationResult", "CompanyAdministrationService", "CompanyAdministrationView",
    "CompanyAuditItem", "CompanyAuditService", "CompanyAuditView", "CompanyCapabilityAccess", "CompanyDashboardService", "CompanyDashboardSnapshot", "CompanyDashboardView",
    "CompanyNavigationService", "CompanyNavigationView", "CompanyNotificationItem", "CompanyNotificationsService", "CompanyNotificationsView", "CompanyPermissionView",
    "CompanyPlatformCapabilities", "CompanyPlatformContract", "CompanyPlatformContext", "CompanyReportDefinitionView", "CompanyReportResultView", "CompanyReportingService",
    "CompanyReportingView", "CompanyRoleAction", "CompanyRoleAdministrationExecutor", "CompanyRoleAdministrationRequest", "CompanyRoleAdministrationService", "CompanyRoleView",
    "CompanyRolesPermissionsService", "CompanyRolesPermissionsView", "CompanyUserAction", "CompanyUserAdministrationExecutor", "CompanyUserAdministrationOperationService", "CompanyUserAdministrationRequest",
    "CompanyUserAdministrationService", "CompanyUserView", "CompanyUsersView", "CompanyVisibilityAction", "CompanyVisibilityAdministrationExecutor", "CompanyVisibilityAdministrationRequest",
    "CompanyVisibilityAdministrationResult", "CompanyVisibilityAdministrationService", "DataVisibilityAdministrationService", "DataVisibilityRuleView", "DataVisibilityView",
    "CompanyWorkspaceAdministrationService", "CompanyWorkspacesView", "WorkspaceView",
]
