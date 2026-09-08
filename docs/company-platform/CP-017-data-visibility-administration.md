# CP-017 — Company Platform Data Visibility Administration

## Purpose

CP-017 adds the controlled Company Platform administration boundary for tenant data-visibility rules.

Supported operations are:

- Create visibility rule
- Update visibility rule
- Enable rule
- Disable rule
- Add role scope
- Remove role scope
- Update resource scope

## Authority boundary

Company Platform is implemented in the Phoenix Generic Framework. It does not become an authorization engine and does not persist visibility rules.

The Framework creates an immutable, tenant-bound request and delegates the mutation to an authoritative application executor. Phoenix Core and the relevant business-domain service remain authoritative for authorization semantics, enforcement, persistence, audit, and security context.

CP-006 remains the read-only presentation projection for existing visibility rules.

## Tenant isolation

Every request is bound to the organisation in the authenticated `CompanyPlatformContext`. Execution rejects a request whose organisation does not match the current context.

Cross-tenant rule administration is therefore prohibited at the Framework boundary.

## Validation

Existing-rule operations require a `rule_id`. Role-scope operations require a `role_scope`, while rule creation, rule updates, and resource-scope updates require a `resource_scope`.

These checks validate request shape only. They do not determine whether a role is actually permitted to see a resource.

## Security and audit

The Framework requires an authenticated, tenant-bound context. Final authorization must be performed by the authoritative Core/application executor. Mutations must preserve the Core security, correlation, tenant, and audit context.

No duplicate permission engine, visibility database, or audit store is introduced.

## Testing

`tests/test_company_visibility_admin_cp017.py` covers tenant binding, immutability, required identifiers/scopes, cross-tenant rejection, executor delegation, and unauthenticated access.

Tests were added but were not executed in the available GitHub-only environment.
