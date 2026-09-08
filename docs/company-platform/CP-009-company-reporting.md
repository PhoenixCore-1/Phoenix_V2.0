# CP-009 — Company Reporting

## Purpose

CP-009 establishes the Company Platform reporting presentation and orchestration boundary for tenant-level oversight and reporting.

## Surface

The Framework may present report definitions and tenant-scoped report results supplied by authoritative Core or business-module reporting services. A report definition identifies the report, display metadata and authoritative source. Results are immutable projections containing generated time, columns and rows.

## Authority

Phoenix Core remains authoritative for identity, tenant context, authorization and entitlements. Business modules remain authoritative for their domain reporting data. The Framework does not create a competing reporting database or reporting rules engine.

## Tenant isolation

Every report definition and result projection requires authenticated, tenant-bound Company Platform context. Cross-tenant report data is rejected.

## Authorization

Report visibility and execution must be decided by the authoritative Core/module service. Framework metadata such as `permitted` is descriptive and must never grant access by itself.

## Mutation and execution boundary

Future report execution, scheduling, exports and report configuration actions must use authorised application services and existing Core job/integration infrastructure where applicable. The Framework must not write directly to Core or module persistence.

## UI implication

The Company Platform Reporting screen may catalogue available company reports, show permitted report results, present filters/metadata supplied by authoritative services, and provide navigation to report outputs. It must preserve tenant, identity, permission and entitlement context for every request.
