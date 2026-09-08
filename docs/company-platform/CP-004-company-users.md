# CP-004 — Company Users Administration

## Purpose

CP-004 establishes the Company Platform user-administration presentation and orchestration boundary for tenant administrators.

## Authority

Phoenix Core remains authoritative for identity, authentication, organisation membership, permissions, entitlements and security context. Company Platform does not create a parallel user store or duplicate identity authority.

## Surface

The Framework surface provides read-only projections of Core-supplied `UserContext` values for the current organisation. It supports both a single-user view and a tenant-scoped collection view.

## Tenant isolation

Every projection requires an authenticated, tenant-bound `CompanyPlatformContext`. A user whose `organisation_id` differs from the current request organisation is rejected.

## Out of scope

CP-004 does not directly create, delete, authenticate, deactivate, assign authoritative memberships, or persist identities. Mutating identity or membership operations must be exposed by authoritative Core services and consumed through controlled application/service boundaries.

## UI implication

The eventual Company Platform Users screen may present user identity, display name, permissions and entitlements supplied by Core, while action controls must invoke authorised Core services rather than Framework persistence.
