# CP-005 — Roles & Permissions Administration

## Purpose

CP-005 establishes the Company Platform presentation and orchestration boundary for tenant roles and permissions.

## Authority

Phoenix Core remains authoritative for authorization, permission definitions, security policy and enforcement. Company Platform does not create a second authorization engine or persist duplicate permission rules.

## Surface

The Framework exposes read-only projections for roles and permissions supplied by authoritative services. A role contains its identifier, name, description, tenant and permission codes. A permission contains its stable code, display name and description.

## Tenant isolation

All role projections require an authenticated, tenant-bound `CompanyPlatformContext`. Roles belonging to another organisation are rejected.

## Mutation boundary

Future create/update/delete or role-assignment actions must invoke authorised Core application services. This Framework layer must not write directly to Core persistence.

## UI implication

The Company Platform Roles & Permissions screen may display role-to-permission mappings and provide authorised action controls, but authorization decisions and persistence remain in Phoenix Core.
