# Phoenix Account 360 — Core V2 Runtime Integration V1.0

## Purpose

This integration connects the independently deployed Phoenix Account 360 module to Phoenix Core V2 without transferring ownership of Account 360 business data or business rules into Core.

## Ownership boundary

**Phoenix Core V2 owns:**
- module registration metadata;
- module lifecycle state (`REGISTERED`, `ENABLED`, `DISABLED`, `RETIRED`);
- Core module identity and registry persistence;
- the runtime boundary used to verify the external package.

**Account 360 owns:**
- Account 360 domain logic;
- Account 360 database/schema and projections;
- financial/commercial/operational 360 behaviour;
- its own service adapters and cross-module contracts.

Core does not directly access Account 360 tables.

## Runtime verification

Core receives an explicit Account 360 deployment path and verifies that the package exists at that path. It then validates the public package metadata:

- code: `account_360`
- name: `Account 360`
- version: `1.0.0`

An unavailable package or metadata mismatch prevents registration/enablement.

## Lifecycle

Registration creates the Core module record in `REGISTERED` state. Enable/disable operations are delegated to the authoritative Core `ModuleService`. Account 360 is not implicitly enabled merely because its package is present.

## Failure behaviour

- Missing deployment path/package: fail closed.
- Import failure: fail closed.
- Metadata mismatch: fail closed.
- Duplicate registration: preserve Core registry uniqueness and surface an integration error.
- Core lifecycle transition errors: preserve Core lifecycle rules.

## Verification gate

The runtime integration is considered ready for the next integration layer only after the dedicated runtime tests pass together with the complete Core V2 regression suite.
