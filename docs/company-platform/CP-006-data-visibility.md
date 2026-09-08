# CP-006 — Data Visibility Administration

## Purpose

CP-006 establishes the Company Platform presentation and orchestration boundary for tenant-level data visibility administration.

## Authority

Phoenix Core remains authoritative for authorization, security context and enforcement. Business modules remain authoritative for domain-specific access rules. Company Platform does not create a second authorization engine or persist duplicate enforcement rules.

## Surface

The Framework exposes read-only visibility-rule projections containing the rule identity, resource, scope, permitted roles, enabled state and tenant. It also provides a tenant-scoped collection view.

## Tenant isolation

All projections require an authenticated, tenant-bound `CompanyPlatformContext`. Rules belonging to another organisation are rejected.

## Mutation boundary

Future visibility-rule changes must invoke the appropriate authorised Core or domain service. The Framework must never write directly to persistence or bypass module/domain authorization.

## UI implication

The Company Platform Data Visibility screen may present effective visibility configuration and authorised controls. Enforcement continues to occur at the authoritative Core/domain boundary for every request.
