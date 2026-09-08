# CP-028 — Company Platform Module Experience Administration

## Purpose

CP-028 adds the controlled Company Platform administration boundary for tenant-level module presentation and user experience configuration.

Supported operations:

- Set module visibility
- Update module navigation presentation
- Enable / disable a module within a company workspace
- Update module presentation metadata
- Set a module default view

## Authority boundary

The Framework configures tenant presentation and experience metadata only. It does not activate, remove, upgrade, downgrade, license or otherwise change module lifecycle state. Phoenix Core and Phoenix System remain authoritative for module availability, licensing, entitlements and access control.

## Tenant isolation

Every request is bound to the authenticated organisation. Cross-tenant requests are rejected before delegation.

## Access and entitlements

Module visibility, navigation and workspace configuration are presentation controls. They never grant permissions or entitlements. Core entitlement and authorization checks remain the final authority for access.

## Module authority

The Framework treats module codes and presentation values as opaque references. Module-specific business semantics remain owned by the relevant business module. The Framework does not create a duplicate module registry or module persistence store.

## Persistence and execution

The Framework creates immutable requests and delegates changes to an authoritative application executor. It does not introduce a separate persistence layer, authorization engine, licensing engine or module lifecycle service.

## Testing

`tests/test_company_module_experience_admin_cp028.py` covers tenant binding, immutability, module/workspace validation, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
