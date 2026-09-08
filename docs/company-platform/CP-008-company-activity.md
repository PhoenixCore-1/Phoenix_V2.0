# CP-008 — Company Activity

## Purpose

CP-008 establishes the Company Platform activity overview presentation boundary for tenant administrators.

## Scope

The activity surface can present tenant-scoped activity items with timestamp, category, summary, actor identity and source. It supports an overview of meaningful company activity without becoming the authoritative event or audit store.

## Authority

Authoritative events and audit records remain owned by Phoenix Core or the relevant business module. The Framework consumes authorised projections from those sources and presents/orchestrates them for the Company Platform.

## Tenant isolation

Every activity item and activity collection is bound to the current authenticated tenant context. Cross-tenant activity is rejected.

## Security

Authentication and tenant binding are required. Permission and entitlement enforcement remains in Core and the relevant source service; activity presentation metadata does not grant access.

## Persistence boundary

No Company Platform activity database or duplicate event store is introduced. Future filtering, pagination and aggregation should operate through authoritative service/query boundaries.
