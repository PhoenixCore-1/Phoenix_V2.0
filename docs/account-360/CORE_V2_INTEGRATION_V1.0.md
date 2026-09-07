# Phoenix Account 360 V1.0 — Phoenix Core V2 Integration

## Integration target

Phoenix Core V2.0 is the authoritative platform host. Account 360 V1.0.0 remains an independently packaged module.

## Core ownership

Phoenix Core V2 owns module registration, tenant isolation, authentication/authorization, licensing, navigation, audit, configuration and platform-level service transport.

## Account 360 ownership

Account 360 owns its Account 360 domain contracts, projections, timeline, workflows, UI presentation model and domain-specific AI orchestration. It does not become a Core system of record.

## Registration

- code: `account_360`
- name: `Account 360`
- version: `1.0.0`
- route: `/account-360`
- default enabled: `false`
- external package: `account_360`

## Deployment boundary

Core stores only module metadata and lifecycle state. Account 360 application code/data are deployed and operated as an external module through the Phoenix V2 module integration boundary.

No Account 360 tables are merged into Core's platform database as a substitute for the module's own data boundary.

## Release gate

The integration branch must pass the Core V2 regression suite and the Account 360 V1.0 regression suite before merge to the Core V2 mainline.
