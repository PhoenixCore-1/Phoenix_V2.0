# CP-018 — Company Platform Workspace Administration

## Purpose

CP-018 adds the controlled administration boundary for company workspaces.

Supported operations:

- Create workspace
- Update workspace
- Activate workspace
- Deactivate workspace
- Set default workspace
- Update workspace navigation composition
- Update workspace dashboard composition

## Authority boundary

Company Platform remains part of the Phoenix Generic Framework. Workspace configuration is presentation/orchestration metadata and is not a replacement for Core authorization, tenancy, identity, permissions, or entitlements.

The Framework builds immutable tenant-bound requests and delegates mutations to an authoritative application executor. No workspace persistence or second authorization engine is introduced.

The existing CP-007 workspace views remain the read-only projection boundary.

## Validation

Operations affecting an existing workspace require `workspace_id`. Workspace creation/update requires workspace parameters. Navigation and dashboard composition updates require their respective key collections.

These validations check request shape only. They do not grant access to navigation items, dashboards, modules, or business capabilities.

## Security

Requests require an authenticated, tenant-bound `CompanyPlatformContext` and reject cross-tenant organisation identifiers. Final authorization and enforcement remain with the authoritative Core/application service.

Mutation execution must preserve Core security, tenant, correlation, and audit context.

## Testing

`tests/test_company_workspace_admin_cp018.py` covers tenant binding, immutability, required identifiers and composition data, cross-tenant rejection, executor delegation, and unauthenticated access.

Tests were added but were not executed in the available GitHub-only environment.
