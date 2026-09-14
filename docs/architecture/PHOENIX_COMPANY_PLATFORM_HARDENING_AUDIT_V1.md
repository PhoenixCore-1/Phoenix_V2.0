# Phoenix Company Platform — Hardening Audit V1

**Status:** Hardening verification / release gate
**Branch:** `feature/core-http-api-v1`
**Date:** 2026-09-14

## Scope

This audit verifies the Company Platform against the locked Phoenix architecture:

- Phoenix Core remains the sole identity, tenant, permission, entitlement and audit authority.
- Company Platform remains tenant-level administration and oversight, not a second Phoenix control plane.
- HTTP transport does not become a persistence or business authority.
- Company Platform legal/compliance behavior consumes the appropriate Core/System Platform legal framework rather than create a competing authority.

## Findings and actions completed

### 1. Authentication and tenant context — PASS

Browser authentication uses the Core session cookie and request context is resolved server-side. The browser does not supply authoritative identity, organisation, permissions or entitlements.

### 2. Company mutation authorization — PASS

People & Access mutations require Company Platform permissions and validate the target membership, role or user against the current organisation before mutation.

### 3. Company activity — PASS

Activity is sourced from the Core Audit service and is tenant-scoped through the resolved request context. Identity filters are additionally checked against memberships in the current organisation.

### 4. Company reports — HARDENED

Reports are explicitly scoped to Company Administration and are routed through a Company Platform application-service boundary rather than implementing reporting logic in the HTTP adapter.

### 5. Company workspaces — HARDENED

Workspace HTTP routes no longer construct the workspace service or record audit events directly in the transport adapter. Workspace behavior is behind the Company Platform application-service boundary.

### 6. Company Platform read authorization — HARDENED

People & Access read surfaces require the relevant Company Platform administration permission. This prevents an authenticated ordinary tenant member from enumerating company users, memberships, roles and permissions merely because they have a valid session.

### 7. Migration bootstrap — HARDENED

A central migration runner applies every checked-in SQL migration in deterministic filename order for the development HTTP application. Company Platform workspace, visibility and permission migrations are therefore included in a fresh development database.

### 8. Company Settings — HARDENED

Company Settings are tenant-scoped and routed through the Core configuration/application boundary. Company configuration permissions are enforced server-side and settings mutations are audited. The Company Platform does not gain authority over platform licensing or module activation through this surface.

### 9. Company Visibility — HARDENED

Company Visibility is behind a Company application-service boundary. The HTTP transport no longer constructs the persistence service, accesses the Core database directly or records visibility audit events itself.

### 10. Atomic company user provisioning — HARDENED

Company user provisioning is now a Core-authoritative transaction covering identity, user and organisation membership. A failure rolls the transaction back rather than leaving a partially provisioned company user. Company audit events are recorded after successful provisioning.

### 11. CSRF protection — HARDENED

State-changing authenticated browser requests require a same-origin `Origin` check at the Core HTTP boundary. The session cookie remains `HttpOnly`, `Secure` and `SameSite=Lax`.

### 12. Typed HTTP request models — HARDENED

HTTP request payloads for the hardened Company Platform surfaces use typed Pydantic request models and standard FastAPI validation rather than raw JSON mutation payload handling.

### 13. Core application boundary — HARDENED

Company Platform HTTP routes are progressively consolidated behind CoreApi and Company Platform application-service methods. Company Visibility was the remaining identified HTTP surface performing direct persistence/service construction and has now been moved behind an application boundary.

## Regulatory / Legal boundary

The Company Platform uses the Phoenix legal/policy foundation already owned by Core and the System Platform framework. It must not create a second legal document, acceptance, audit, identity or regulatory authority.

ADR-040 establishes Phoenix Core as authoritative for platform policy state, acceptance records, enforcement state and audit integration, while legal content remains controlled by the appropriate legal/commercial authority.

V2.0 explicitly excludes ERP compliance, SARS integration/submissions, tax compliance platforms, VAT automation, broad regulatory compliance frameworks, advanced legal contract lifecycle management and general-purpose governance/risk/compliance functionality. These are not Company Platform hardening requirements for Core V2.0.

Company Platform may consume future published regulatory/legal requirements through approved Core/System Platform contracts when such capabilities are formally introduced. It must not invent a competing compliance authority in V2.0.

## Remaining release gates

### 1. Automated execution — RELEASE GATE

The complete automated test suite must be executed against the actual `feature/core-http-api-v1` branch after the latest hardening changes. No current passing count is claimed until that execution occurs.

### 2. End-to-end browser flow — RELEASE GATE

The actual frontend must be verified through:

`login → Core session → Company Platform → tenant context → authorization → Company workspace`

This must be tested against the current integrated frontend/backend rather than inferred from individual endpoint tests.

## Gate decision

**Company Platform is not yet declared fully locked.**

The architectural and application-boundary hardening identified during this audit has been implemented. The remaining blockers are verification gates: full automated execution and actual browser end-to-end verification.

No broader ERP/SARS/tax compliance layer should be added merely to close this audit.
