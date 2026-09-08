# CP-020 — Company Platform User Data Visibility Administration

## Purpose

CP-020 adds the controlled Company Platform boundary for user-specific data-visibility assignments and exceptions.

Supported operations:

- Grant user visibility scope
- Revoke user visibility scope
- Set user visibility
- Clear user visibility

## Authority boundary

The Framework creates an immutable tenant-bound request and delegates all mutations to an authoritative application executor. It does not persist user visibility rules and does not implement a second authorization engine.

Phoenix Core and the relevant business-domain service remain authoritative for identity, tenant membership, authorization semantics, persistence, enforcement, audit and security context.

## Tenant isolation

Every request is bound to the organisation in the authenticated `CompanyPlatformContext`. Execution rejects requests belonging to another organisation.

The authoritative executor must additionally validate that the target identity and resource belong to, or are valid within, the current tenant.

## Scope semantics

The Framework treats `resource` and `scope` as opaque policy identifiers. It validates only that required values are present. It does not decide whether a scope grants or denies access.

User-level visibility must never bypass higher-level authorization, licensing, entitlement or security controls.

## Security and audit

All operations require an authenticated, tenant-bound context. Final authorization and mutation occur through the authoritative executor, which must preserve Core correlation, security and audit context.

## Relationship to CP-006 and CP-017

CP-006 provides read-only tenant visibility-rule projections. CP-017 provides administration of shared visibility rules. CP-020 provides user-specific visibility administration without changing either authoritative boundary.

## Testing

`tests/test_company_user_visibility_cp020.py` covers tenant binding, immutability, required identity/resource/scope values, cross-tenant rejection, executor delegation and unauthenticated access.

Tests were added but were not executed in the available GitHub-only environment.
