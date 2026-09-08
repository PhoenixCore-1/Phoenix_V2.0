# CP-025 — Company Platform Document Administration

## Purpose

CP-025 adds the controlled Company Platform boundary for tenant document administration.

Supported operations include document-category administration, document metadata updates, visibility configuration and requests for upload, download, deletion and new versions.

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates them to the authoritative Core/document application service. It does not own file storage, document persistence, access enforcement, version storage or binary transfer.

## Tenant isolation

Every request is bound to the authenticated organisation. Cross-tenant requests are rejected before delegation.

## Visibility

The Framework accepts visibility scope as an opaque administration value. It does not implement a second authorization engine. Core and the authoritative document/domain service remain responsible for deciding and enforcing access.

## Categories and metadata

Category and metadata operations are configuration requests only. The Framework does not maintain a document-category or metadata database.

## File operations

Upload, download, delete and version operations are represented as controlled requests. Actual storage and file handling remain behind the authoritative document service and must preserve Core security, tenant, audit and access context.

## Testing

`tests/test_company_document_admin_cp025.py` covers tenant binding, immutability, required category/document targets, required parameters, visibility validation, cross-tenant rejection, executor delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
