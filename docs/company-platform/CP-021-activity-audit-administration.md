# CP-021 — Company Platform Activity & Audit Administration Controls

## Purpose

CP-021 adds the controlled Company Platform boundary for searching, filtering and requesting exports of company activity and audit information, plus read-only retention-policy viewing.

Supported operations:

- Search activity
- Search audit records
- Request activity export
- Request audit export
- View retention policy

## Authority boundary

The Framework does not store activity or audit records and does not mutate audit data. It creates an immutable, tenant-bound request and delegates execution to an authoritative Core/application service.

Phoenix Core remains authoritative for audit generation, integrity, retention policy, security context and access enforcement. Business modules remain authoritative for their domain activity records.

## Filtering

Filters are passed as opaque key/value criteria. The Framework does not reinterpret business-domain semantics or use filters to bypass authorization.

## Export

Exports are requests, not direct file generation. The authoritative executor decides whether the actor is permitted to export the requested information and should use the Core job/integration infrastructure where asynchronous processing is required.

An export format is mandatory for export requests and prohibited on search or retention-view requests.

## Retention

`VIEW_RETENTION_POLICY` is deliberately read-only. CP-021 does not provide a retention-policy mutation operation because retention authority belongs to Core. Any future retention-policy administration must be introduced through an explicit Core-authorized contract rather than a Framework-local policy engine.

## Tenant isolation and security

All requests require an authenticated, tenant-bound `CompanyPlatformContext`. Cross-tenant requests are rejected before delegation. The authoritative executor remains responsible for final authorization and preservation of correlation, security and audit context.

## Testing

`tests/test_company_activity_audit_admin_cp021.py` covers tenant binding, immutability, export-format validation, cross-tenant rejection, executor delegation and unauthenticated access.

Tests were added but were not executed in the available GitHub-only environment.
