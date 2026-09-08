# CP-016 — Company Platform Role & Permission Administration

## Purpose

CP-016 defines the controlled Company Platform operation boundary for role lifecycle and role-permission administration.

## Supported operations

- Create role
- Update role
- Activate role
- Deactivate role
- Grant permission to role
- Revoke permission from role

## Authority boundary

Requests are immutable and tenant-bound. The Framework constructs and validates requests, then delegates execution to an authoritative Core application executor. Company Platform does not persist roles or permissions and does not implement a second authorization engine.

## Validation

Role lifecycle operations that act on an existing role require a role identifier. Permission grant/revoke operations require both a role identifier and permission code. Requests must match the authenticated tenant context.

## Security

The caller must have an authenticated, tenant-bound Company Platform context. Final authorization, role semantics, permission validity, audit, transactionality and persistence remain authoritative in Core.

## Relationship to CP-005

CP-005 remains the read-only presentation projection for roles and permissions. CP-016 adds the mutation request/executor boundary without changing that projection responsibility.
