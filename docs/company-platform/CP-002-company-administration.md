# CP-002 — Company Administration Foundation

## Boundary

Company Administration is a Phoenix Generic Framework presentation/orchestration boundary. Phoenix Core remains authoritative for company/tenant identity and state.

## V1.0 surface

- Company Profile
- Company Status
- Tenant Overview
- Company Settings presentation boundary

## Security and tenancy

Every operation requires an authenticated, tenant-bound Framework context. The company context supplied to the view must belong to the current organisation. Cross-tenant projection is rejected.

## Authority rules

The Framework does not create or own a second company/tenant record. It does not own identity, authorization, licensing, audit authority, or business transactions.
