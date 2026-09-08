# CP-012 — Company Platform Administration Actions

## Purpose

CP-012 establishes the controlled mutation boundary for Company Platform administration. Company Platform builds immutable, tenant-bound administration requests and delegates execution to an authoritative application service.

## Supported action domains

- User administration
- Role and permission administration
- Data visibility administration
- Workspace administration

## Authority boundary

Company Platform does not own identity, membership, authorization, visibility, workspace persistence, audit records, or business transactions. It does not implement a second mutation engine.

The supplied `CompanyAdministrationExecutor` represents the authoritative Core application boundary. The Framework facade validates authentication and tenant binding, then delegates the request without changing its meaning.

## Security and tenant isolation

- An authenticated, tenant-bound Company Platform context is required.
- Every request carries the originating organisation ID.
- A request cannot be executed under a different organisation context.
- Parameters are immutable and normalized for deterministic transport.
- The executor remains responsible for the authoritative permission decision and mutation rules.
- Mutations must preserve Core security, audit, correlation and tenant context.

## No direct persistence

No Company Platform database or duplicate identity/role/visibility/workspace store is introduced by CP-012. UI and Framework code must not access Core persistence directly.

## Future implementation

When authoritative Core application services exist for a specific mutation, the corresponding executor may adapt the Company Platform request to that service. Until then, CP-012 intentionally defines the contract rather than inventing duplicate Core business logic.

Future mutation flows should use Core authorization and audit infrastructure and should support idempotency where the operation is retryable.
