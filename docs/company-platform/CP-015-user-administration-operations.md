# CP-015 — Company Platform User Administration Operations

## Purpose

CP-015 defines the Framework-level contract for controlled Company Platform user administration.

## Supported operations

- Invite a user
- Activate an existing identity
- Deactivate an existing identity
- Assign a role
- Remove a role

## Authority boundary

The Framework creates immutable, tenant-bound requests and delegates execution to an authoritative Core application boundary. It does not create identity records, memberships, roles, permissions or authentication state itself.

Invitation may identify a prospective user through request parameters. Existing-user operations require an identity ID. Role assignment/removal requires a role ID.

## Security

Requests require an authenticated, tenant-bound Company Platform context. Requests cannot be replayed against another organisation. The authoritative executor remains responsible for final authorization, membership validation, audit, correlation, idempotency and persistence.

## Compatibility

The existing CP-004 read-only `CompanyUserAdministrationService` remains unchanged. CP-015 adds the separate `CompanyUserAdministrationOperationService` so read projection and mutation orchestration do not become conflated.
