# CP-023 — Company Platform Notification Administration

## Purpose

CP-023 adds the controlled Company Platform administration boundary for notification preferences, notification channels/types, notification actions and user notification state.

Supported operations:

- Update company notification preferences
- Update user notification preferences
- Enable / disable delivery channels
- Enable / disable notification types
- Send a notification request
- Mark notification read/unread
- Dismiss a notification

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates authoritative notification configuration and delivery operations to Core notification services. It does not persist notifications, implement a delivery engine, or replace Core security/authorization.

## Tenant and user isolation

Every request is bound to the authenticated organisation. User-targeted operations identify the target identity explicitly, while notification state operations also identify the notification. Core remains authoritative for membership and authorization checks.

## Delivery and security

Channel configuration and notification delivery are request boundaries only. Actual email, in-app, SMS or other delivery mechanisms remain outside this Framework layer and must use the authoritative Core notification infrastructure and security controls.

## Relationship to CP-011

CP-011 remains the read-only notification-centre projection. CP-023 provides controlled administration/action requests without duplicating notification persistence or delivery infrastructure.

## Testing

`tests/test_company_notifications_admin_cp023.py` covers tenant binding, immutability, required targets, parameter validation, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
