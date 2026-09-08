# CP-011 — Company Notifications

## Purpose

CP-011 establishes the Company Platform notification-centre presentation boundary for tenant users and administrators.

## Scope

The Framework projects authoritative notification records with creation time, title, message, category, severity, recipient, read state, source and optional navigation target. Unread count is derived from the supplied projection.

## Authority

Company Platform does not create a notification engine or notification store. Notification generation, persistence, delivery, targeting and authoritative read-state mutation remain outside this presentation boundary and must be supplied by authoritative Core/application services.

Phoenix Core already provides communications and realtime foundations; these remain separate from the Company Platform presentation model.

## Tenant isolation

Every notification projection requires an authenticated, tenant-bound Company Platform context. Cross-tenant notifications are rejected for both individual records and collections.

## Read/unread boundary

The `read` flag is treated as authoritative input. Company Platform may display unread counts and filters, but it does not mutate notification state directly. A future mark-read/mark-unread action must call the authoritative application service and preserve the normal security, tenant and audit context.

## Delivery boundary

Email, push, realtime and other delivery mechanisms are infrastructure concerns. The Company Platform UI must not implement or bypass delivery services.

## UI implication

The Notifications screen may provide unread/all filters, severity/category filtering, timestamps, source labels and navigation to authorised targets. The top-level Phoenix notification indicator may consume the same tenant-scoped projection and unread count.

## Testing boundary

CP-011 tests cover projection, tenant isolation, derived unread count, immutability and authenticated tenant context. Tests are committed but are not claimed as executed because the connected GitHub environment does not expose a runnable pytest environment.
