# Phoenix Core V2

Phoenix Core V2 is the authoritative foundation of the Phoenix platform.

## Architectural Principle

> V1 is the teacher; V2 is the new system.

Phoenix Core V2 is a clean rebuild and is not a direct copy of Phoenix Core V1.

## Core Responsibilities

Phoenix Core owns platform-wide foundational capabilities including:

- Identity
- Authentication
- Organisations and tenant authority
- Organisation membership
- Roles
- Permissions
- Sessions
- Security
- Module registry
- Technical entitlements
- Audit infrastructure
- Core APIs and contracts

Business modules own their own business-domain data and rules.

## Core Rules

- One Phoenix Core authority
- One authoritative data owner per domain
- Strict tenant isolation
- No direct database access from clients or modules
- Server-side authorization
- Authentication, authorization and licensing remain distinct
- Core remains extensible
- Business modules remain independently extensible
- V1 remains reference-only
- Production databases are never committed to Git
- Secrets are never committed to Git
- Architecture decisions are documented and preserved

## Project Structure

src/
    phoenix_core/

tests/

migrations/

docs/
    architecture/
        adr/

scripts/

## Development Status

Phoenix Core V2 is currently in the foundation architecture and implementation phase.

The first implementation target is the Core identity, organisation, membership, authentication, session and authorization foundation.
