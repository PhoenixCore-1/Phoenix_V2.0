# CP-019 — Company Platform User Workspace Assignment

## Purpose

CP-019 adds the controlled Company Platform boundary for assigning tenant users to workspaces and managing their default workspace.

Supported operations:

- Assign workspace to user
- Remove workspace from user
- Set default workspace for user
- Clear default workspace for user

## Authority boundary

The Framework creates an immutable tenant-bound assignment request and delegates mutation to an authoritative application executor. It does not persist assignments or implement a second membership or authorization system.

Phoenix Core remains authoritative for identity, organisation membership, authorization, entitlements and security. The authoritative application layer must validate that the identity and workspace belong to the current tenant and that the actor is allowed to administer the assignment.

## Tenant isolation

Every request is bound to the organisation in the authenticated `CompanyPlatformContext`. Execution rejects requests from another organisation.

## Default workspace

A default workspace is a user experience preference/configuration, not an authorization grant. Setting or clearing a default workspace must not expand the user's permissions or entitlements.

## Security and audit

All operations require an authenticated, tenant-bound context. The authoritative executor is responsible for final authorization, persistence, audit, correlation and any membership/business rules.

## Relationship to CP-007 and CP-018

CP-007 provides the read-only workspace configuration projection. CP-018 provides controlled workspace administration. CP-019 handles user-to-workspace assignment and default-workspace configuration without duplicating either authority.

## Testing

`tests/test_company_workspace_assignments_cp019.py` covers tenant binding, immutability, required identity/workspace values, cross-tenant rejection, executor delegation and unauthenticated access.

Tests were added but were not executed in the available GitHub-only environment.
