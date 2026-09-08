# CP-013 — Company Platform Navigation & Workspace Resolution

## Purpose

CP-013 establishes the Company Platform presentation boundary for resolving tenant navigation and the active workspace.

## Navigation

Navigation is resolved from existing Framework `NavigationContract` metadata. Disabled items are omitted. Permission and entitlement metadata are evaluated against the authenticated Core-derived `CompanyPlatformContext` for presentation visibility only.

Navigation metadata does not grant authorization. Final access remains authoritative in Phoenix Core and the relevant application service/module.

## Workspaces

Workspace selection is tenant-scoped. A default workspace is preferred; otherwise the first tenant workspace is selected. A workspace belonging to another organisation cannot be used for navigation resolution.

## Boundary

The Company Platform does not create a second navigation registry, authorization engine, entitlement engine or workspace persistence layer. Existing Core and Framework contracts remain authoritative.

## UI implications

The Platform UI can consume the resolved navigation/workspace view to render the Company Platform shell, sidebar and workspace experience. Navigation must integrate with the existing Phoenix Core navigation/back-stack behaviour rather than implementing an independent history mechanism.

## Security

Resolution requires an authenticated, tenant-bound context. Cross-tenant workspaces are rejected. Permission and entitlement checks are derived from Core security context.
