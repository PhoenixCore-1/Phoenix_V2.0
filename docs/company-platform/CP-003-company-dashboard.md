# CP-003 — Company Dashboard / Tenant Overview

## Purpose

CP-003 provides the Company Platform landing experience: a read-only administrative overview of the current tenant. It is a Framework presentation/orchestration surface, not a business-transaction dashboard.

## Dashboard surface

The dashboard may present:

- Company name and active/inactive status.
- Total users and active-user indicators.
- Recent activity indicators supplied by authoritative platform services.
- Modules visible to the current tenant/user context.
- Administrative attention items supplied by authoritative services.

## Authority and boundaries

- Phoenix Core remains authoritative for identity, organisation/tenant context, authorization, licensing/entitlements, security and audit authority.
- Business modules remain authoritative for business transactions and business-domain metrics.
- The Company Platform does not store a duplicate company, user, module, licensing or transaction dataset.
- Module visibility is projection metadata supplied to the dashboard; the dashboard cannot activate, remove, upgrade or downgrade modules.
- All dashboard access requires an authenticated, tenant-bound CompanyPlatformContext.
- Cross-tenant company context is rejected.
- No direct database access is permitted.

## Data contract

`CompanyDashboardSnapshot` is an immutable input contract for summary data. Counts, visible module descriptors and attention items are supplied by authoritative services and are not persisted by the dashboard.

## Non-goals

CP-003 does not implement:

- business transaction initiation, approval or execution;
- module activation or licensing administration;
- tenant persistence;
- replacement authorization rules;
- replacement audit authority;
- business-domain reporting.
