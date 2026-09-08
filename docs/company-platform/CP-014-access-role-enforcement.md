# CP-014 — Company Platform Access & Role Enforcement

## Purpose

CP-014 defines the Company Platform access boundary using the authenticated, tenant-bound security context supplied by Phoenix Core.

## Enforcement model

Company Platform access is derived from Core-authoritative permissions. The Framework may evaluate whether a capability is visible or whether a requested operation may proceed through the Company Platform boundary, but it does not own roles, permissions, memberships, authentication or authorization persistence.

`CompanyAccessService.require_access()` rejects requests without the required Core-derived permission. `can_access()` provides a boolean presentation decision. Capability evaluation is immutable and descriptive.

## Navigation

Navigation filtering applies the same Core-derived permission and entitlement context for presentation. Hidden navigation does not itself constitute authorization, and direct requests must still be authorized by the authoritative application service.

## Boundary

No Company Platform role table, permission engine, membership store or entitlement engine is introduced. Company Platform roles and permissions remain projections of Core authority.

## Security

All access requires an authenticated, tenant-bound Company Platform context. Tenant isolation is preserved through that context. Mutating Company Platform actions continue through the CP-012 executor boundary so authoritative Core application services can enforce authorization and audit requirements.
