# CP-010 — Company Audit Presentation

## Purpose

CP-010 establishes the Company Platform audit viewing boundary for tenant administrators.

## Scope

The Framework presents authorised audit records with timestamp, action, resource, actor, outcome and tenant context. Audit records are immutable presentation projections.

## Authority

Phoenix Core remains authoritative for audit capture, integrity, retention, security and access policy. The Framework does not create a second audit engine, audit database or audit authority.

## Tenant isolation

Every audit record and audit collection requires an authenticated, tenant-bound Company Platform context. Cross-tenant audit data is rejected.

## Security

The audit screen is subject to Core authorization and any applicable security policy. Presentation of an audit record does not itself grant access to the underlying resource.

## Mutation boundary

Audit records cannot be edited or deleted through Company Platform. Any administrative audit-management operations, where permitted by the Core architecture, must use authoritative Core services and preserve audit integrity.

## UI implication

The Company Platform Audit screen may provide filtering, sorting, pagination and drill-down navigation over authorised Core audit projections without bypassing tenant, identity or permission boundaries.
