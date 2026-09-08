# CP-027 — Company Platform Workflow Administration

## Purpose

CP-027 adds the controlled Company Platform administration boundary for tenant workflow configuration, assignment and workflow action requests.

Supported operations:

- Enable / disable workflow
- Update workflow configuration
- Assign / unassign workflow
- Start, pause, resume and cancel workflow instances

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates workflow execution to authoritative Core or business-domain application services. It does not become a workflow engine, state store, scheduler or business workflow authority.

## Tenant isolation

Every request is bound to the authenticated organisation. Cross-tenant requests are rejected before delegation.

## Business workflow authority

Workflow state transitions and business-specific workflow semantics remain owned by the relevant Core or business module service. The Framework treats workflow and target identifiers as opaque references.

## Jobs and execution

Any asynchronous workflow execution must use authoritative Core job infrastructure rather than introducing a Framework scheduler.

## Testing

`tests/test_company_workflow_admin_cp027.py` covers tenant binding, immutability, workflow/target validation, configuration requirements, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
