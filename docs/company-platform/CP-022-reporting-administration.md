# CP-022 — Company Platform Reporting Administration

## Purpose

CP-022 adds the controlled Company Platform administration boundary for report definitions, report execution, scheduling and exports.

Supported operations:

- Create report definition
- Update report definition
- Enable / disable report
- Execute report
- Schedule report
- Cancel report schedule
- Export report

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates all report operations to an authoritative Core or business-domain application service. It does not become the reporting engine and does not persist report results.

Core remains authoritative for identity, tenancy, authorization, entitlements, security, jobs and audit. Business modules remain authoritative for domain report definitions and domain report data where applicable.

## Tenant isolation

Every request is bound to the organisation in the authenticated `CompanyPlatformContext`. Cross-tenant requests are rejected before delegation.

## Scheduling and exports

Scheduling is represented as a request containing a schedule parameter; actual scheduling must use the authoritative Core job infrastructure. Export is represented as a request containing an output format; actual export generation remains with the authoritative reporting/application service.

## Security

The Framework validates request shape only. It does not grant report permissions, bypass entitlements, or decide whether a report may expose particular data.

## Relationship to CP-009

CP-009 remains the read-only reporting presentation boundary. CP-022 adds the controlled administration/execution request boundary without duplicating report storage or authorization.

## Testing

`tests/test_company_reporting_admin_cp022.py` covers tenant binding, immutability, report identifiers, definition/scheduling/export validation, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
