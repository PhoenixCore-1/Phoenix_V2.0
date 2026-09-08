"""Phoenix Company Platform V1.0 framework boundary."""

from phoenix_framework.company_platform.administration import (
    CompanyAdministrationService,
    CompanyAdministrationView,
)
from phoenix_framework.company_platform.contracts import (
    COMPANY_PLATFORM_NAVIGATION,
    CompanyPlatformCapabilities,
    CompanyPlatformContract,
)
from phoenix_framework.company_platform.context import CompanyPlatformContext
from phoenix_framework.company_platform.dashboard import (
    CompanyDashboardService,
    CompanyDashboardSnapshot,
    CompanyDashboardView,
)
from phoenix_framework.company_platform.roles import (
    CompanyPermissionView,
    CompanyRoleView,
    CompanyRolesPermissionsService,
    CompanyRolesPermissionsView,
)
from phoenix_framework.company_platform.users import (
    CompanyUserAdministrationService,
    CompanyUserView,
    CompanyUsersView,
)
from phoenix_framework.company_platform.visibility import (
    DataVisibilityAdministrationService,
    DataVisibilityRuleView,
    DataVisibilityView,
)
from phoenix_framework.company_platform.workspaces import (
    CompanyWorkspaceAdministrationService,
    CompanyWorkspacesView,
    WorkspaceView,
)

__all__ = [
    "COMPANY_PLATFORM_NAVIGATION",
    "CompanyAdministrationService",
    "CompanyAdministrationView",
    "CompanyDashboardService",
    "CompanyDashboardSnapshot",
    "CompanyDashboardView",
    "CompanyPermissionView",
    "CompanyPlatformCapabilities",
    "CompanyPlatformContract",
    "CompanyPlatformContext",
    "CompanyRoleView",
    "CompanyRolesPermissionsService",
    "CompanyRolesPermissionsView",
    "CompanyUserAdministrationService",
    "CompanyUserView",
    "CompanyUsersView",
    "DataVisibilityAdministrationService",
    "DataVisibilityRuleView",
    "DataVisibilityView",
    "CompanyWorkspaceAdministrationService",
    "CompanyWorkspacesView",
    "WorkspaceView",
]
