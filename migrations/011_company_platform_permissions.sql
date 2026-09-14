-- Company Platform permissions.
-- These permissions govern tenant-level administration only. They do not grant
-- Phoenix platform-control authority such as licensing or module activation.
INSERT OR IGNORE INTO permissions(id, code, name, created_at) VALUES
    ('company-perm-activity-view', 'company.activity.view', 'View company activity', CURRENT_TIMESTAMP),
    ('company-perm-configuration-manage', 'company.configuration.manage', 'Manage company configuration', CURRENT_TIMESTAMP),
    ('company-perm-memberships-manage', 'company.memberships.manage', 'Manage company memberships', CURRENT_TIMESTAMP),
    ('company-perm-reports-view', 'company.reports.view', 'View company reports', CURRENT_TIMESTAMP),
    ('company-perm-roles-manage', 'company.roles.manage', 'Manage company roles', CURRENT_TIMESTAMP),
    ('company-perm-users-manage', 'company.users.manage', 'Manage company users', CURRENT_TIMESTAMP),
    ('company-perm-visibility-manage', 'company.visibility.manage', 'Manage company data visibility', CURRENT_TIMESTAMP),
    ('company-perm-workspaces-manage', 'company.workspaces.manage', 'Manage company workspaces', CURRENT_TIMESTAMP);
