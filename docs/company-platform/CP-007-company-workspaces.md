# CP-007 — Company Workspaces

## Purpose

CP-007 establishes the Company Platform workspace and UI-configuration presentation boundary for tenant administration.

## Surface

A workspace can expose a stable identifier, display name, permitted navigation keys, dashboard keys, default-workspace state and tenant ownership. The Framework provides read-only projections for one workspace or a tenant-scoped collection.

## Authority

Phoenix Core remains authoritative for identity, tenant context, permissions and entitlements. Navigation and workspace metadata are presentation/orchestration concerns; they do not grant access by themselves.

## Tenant isolation

Every workspace projection requires authenticated, tenant-bound Company Platform context. Cross-tenant workspace data is rejected.

## Mutation boundary

Future workspace create/update/delete and user-workspace assignment actions must use authorised application services. The Framework must not write directly to Core or module persistence.

## UI implication

The Company Platform Workspaces screen may configure dashboard composition, navigation ordering and workspace defaults subject to Core authorization and module entitlement checks. A navigation key or workspace entry must never bypass those checks.
