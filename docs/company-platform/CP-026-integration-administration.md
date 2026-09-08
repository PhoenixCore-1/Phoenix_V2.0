# CP-026 — Company Platform Integration Administration

## Purpose

CP-026 adds the controlled Company Platform administration boundary for tenant integration configuration and connection actions.

Supported operations:

- Enable / disable an integration
- Update integration configuration
- Test connection
- Connect / disconnect
- Refresh connection
- Rotate credentials

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates execution to authoritative Core/integration application services. It does not persist integration connections, store credentials, implement authentication to third-party systems, or execute integrations directly.

## Security

Credentials and secrets are deliberately represented only through an opaque request boundary. Implementations must use the authoritative Core secret/credential handling and never place sensitive credential material in Framework persistence, logs or ordinary UI state.

## Tenant isolation

Every request is bound to the authenticated organisation. Cross-tenant requests are rejected before delegation.

## Integration execution

Connection tests, refreshes, credential rotation and actual integration execution remain authoritative application/integration responsibilities. The Framework is limited to orchestration and administration presentation.

## Testing

`tests/test_company_integration_admin_cp026.py` covers tenant binding, immutability, integration-key validation, configuration requirements, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
