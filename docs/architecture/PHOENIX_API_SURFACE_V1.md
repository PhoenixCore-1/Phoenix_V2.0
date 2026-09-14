# Phoenix Core HTTP API Surface V1

## Status

Architecture contract defining the target HTTP surface between Phoenix Core and Phoenix client applications. An endpoint listed here is not considered live until implemented by an HTTP adapter and covered by tests.

## Authority

Phoenix Core remains the single authority for authentication, sessions, identity, organisation/tenant context, memberships, roles, permissions, module entitlements, audit evidence, Core documents, and legal/compliance evidence.

The frontend must never become an authority for these concerns.

## Transport boundary

```text
Phoenix Core domain/services
        |
     CoreApi
        |
   HTTP API V1
        |
 Phoenix API Client
        |
    Phoenix React UI
```

HTTP handlers must invoke Core application services/contracts. They must not access Core database tables directly. All versioned routes begin with `/api/v1`.

## Request context

Authenticated requests resolve context server-side from the Core session. The browser must not be trusted to supply authoritative identity, organisation, membership, permission, or entitlement values. Each request carries a request/correlation ID so API responses and audit events can be connected.

## Standard response contract

Successful responses use the Core `ApiResponse` contract:

```json
{"data": {}, "request_id": "..."}
```

Errors use the Core `ApiError` contract:

```json
{"code": "AUTHORIZATION_ERROR", "message": "Permission denied.", "request_id": "..."}
```

Known error classes map to validation, not-found, conflict, authentication, authorization, Core, and internal error categories.

## Authentication and session

| Method | Route | Purpose | State |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Authenticate user and establish Core session | TARGET |
| POST | `/api/v1/auth/logout` | Revoke current session | TARGET |
| GET | `/api/v1/auth/session` | Return current session state | TARGET |

The existing Core authentication service and persistent session model remain authoritative. Browser transport must use a secure session mechanism rather than introducing a second authentication system.

## Current context

| Method | Route | Purpose | State |
|---|---|---|---|
| GET | `/api/v1/me` | Current authenticated user context | TARGET |
| GET | `/api/v1/me/identity` | Current Core identity | EXISTING CORE API |
| GET | `/api/v1/me/organisation` | Current organisation | EXISTING CORE API |
| GET | `/api/v1/me/permissions` | Effective permissions | EXTEND |
| GET | `/api/v1/me/entitlements` | Effective module entitlements | EXTEND |

## Memberships, roles and permissions

| Method | Route | Purpose | State |
|---|---|---|---|
| GET | `/api/v1/company/memberships` | Current company memberships | EXTEND |
| GET | `/api/v1/company/roles` | Organisation roles | EXTEND |
| GET | `/api/v1/company/permissions` | Available/effective company permissions | EXTEND |
| POST | `/api/v1/company/users` | Provision company user | EXTEND |
| PATCH | `/api/v1/company/users/{id}` | Update company user | EXTEND |
| POST | `/api/v1/company/memberships/{id}/suspend` | Suspend membership | EXTEND |
| POST | `/api/v1/company/memberships/{id}/restore` | Restore membership | EXTEND |

Every mutation is permission checked server-side and must produce appropriate audit evidence.

## System Platform

System Platform endpoints expose Phoenix platform administration, not tenant business transactions.

```text
GET /api/v1/system/dashboard
GET /api/v1/system/companies
GET /api/v1/system/companies/{id}
GET /api/v1/system/users
GET /api/v1/system/users/{id}
GET /api/v1/system/modules
GET /api/v1/system/modules/{id}
GET /api/v1/system/licensing
GET /api/v1/system/billing
GET /api/v1/system/programmes
GET /api/v1/system/security
GET /api/v1/system/audit
GET /api/v1/system/integrations
GET /api/v1/system/health
GET /api/v1/system/support
GET /api/v1/system/documentation
GET /api/v1/system/settings
GET /api/v1/system/regulatory-legal
```

Mutation endpoints are added only when an authoritative Core service and permission model exist.

## Company Platform

Company Platform is tenant/company administration and cannot become a second platform control plane.

```text
GET /api/v1/company
GET /api/v1/company/users
GET /api/v1/company/roles
GET /api/v1/company/permissions
GET /api/v1/company/workspaces
GET /api/v1/company/modules
GET /api/v1/company/activity
GET /api/v1/company/reports
GET /api/v1/company/compliance
GET /api/v1/company/contracts
GET /api/v1/company/evidence
```

Company context is derived through Core request context and membership validation.

## User Platform

```text
GET /api/v1/user/dashboard
GET /api/v1/user/profile
GET /api/v1/user/preferences
GET /api/v1/user/workspaces
GET /api/v1/user/notifications
GET /api/v1/user/legal
GET /api/v1/user/activity
GET /api/v1/user/security
```

User Platform is the personal workspace and does not replace Core identity/security authority.

## Modules and entitlements

```text
GET /api/v1/modules
GET /api/v1/modules/{code}
GET /api/v1/modules/{code}/access
POST /api/v1/modules/{code}/launch
```

Module access requires appropriate authorization and an active Core entitlement where applicable. Frontend visibility never grants access.

## Documents

```text
GET /api/v1/documents
GET /api/v1/documents/{id}
GET /api/v1/documents/{id}/versions
POST /api/v1/documents
POST /api/v1/documents/{id}/versions
```

Core remains the document and document-version authority. Legal evidence references exact document versions and hashes.

## Legal and compliance

```text
GET /api/v1/legal/requirements
GET /api/v1/legal/required-actions
GET /api/v1/legal/documents/{id}
GET /api/v1/legal/documents/{id}/versions
POST /api/v1/legal/actions/{requirement_id}/complete
GET /api/v1/legal/evidence
GET /api/v1/legal/evidence/{id}
GET /api/v1/legal/history
```

Legal actions are server-side operations. A browser checkbox or client-side state is never the legal evidence authority. Completion must resolve authenticated identity and organisation context from Core and associate the exact legal requirement/document version with immutable evidence and the corresponding Core audit event.

## Audit

```text
GET /api/v1/audit/events
GET /api/v1/audit/events/{id}
```

Audit records are append-only Core evidence. Ordinary application clients cannot modify or delete audit events.

## Notifications and communications

The existing Core communications subsystem is the authority for platform communications. Notifications must be exposed through that subsystem rather than a separate notification authority.

```text
GET /api/v1/notifications
GET /api/v1/notifications/{id}
POST /api/v1/notifications/{id}/read
POST /api/v1/notifications/read-all
```

Delivery channels and realtime transport remain implementation details behind Core communications.

## Search and AI

```text
GET /api/v1/search
POST /api/v1/ai/context
```

Search results must be permission and tenant scoped. AI context must use the same authorization/context rules and never bypass them.

## Module launch context

A module launch request should return the authoritative launch context needed by the UI, including authenticated identity, organisation context, module identity/version, entitlement state, effective module permissions, navigation/workspace metadata, and request/correlation ID. The client must not manufacture this context.

## Implementation classification

### KEEP

- Core authentication service and sessions
- identities/users
- organisations/memberships
- roles/permissions
- module entitlements
- Core audit
- Core documents
- Core communications
- legal policy acceptance foundation

### EXTEND

- CoreApi methods for effective permissions/entitlements
- organisation/user/membership listing APIs
- role and permission APIs
- notifications API
- legal/compliance APIs
- System Platform read models/endpoints
- Company Platform read/write endpoints
- User Platform endpoints

### BUILD

- HTTP/FastAPI adapter
- API routing and dependency/context middleware
- secure browser session transport
- API tests
- React API client

### DO NOT BUILD

- second authentication service
- second tenant/company authority
- frontend-owned permissions
- frontend-owned legal evidence
- direct browser-to-SQL access
- separate platform database that duplicates Core authority

## Definition of done for HTTP API V1

1. Every implemented route is backed by an authoritative Core service.
2. Every authenticated route resolves Core request context server-side.
3. Permission and entitlement checks occur server-side.
4. Tenant isolation is enforced by Core/application services.
5. API errors follow the standard Core error contract.
6. Request IDs propagate through API and audit paths.
7. Mutations create appropriate audit records.
8. No HTTP route accesses Core persistence directly.
9. Browser authentication does not require a second identity/session authority.
10. React can operate entirely through the documented API boundary.
