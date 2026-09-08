# CP-024 — Company Configuration Administration

## Purpose

CP-024 adds a controlled Company Platform boundary for tenant-level company defaults, preferences, presentation features and common display/locale settings.

Supported operations include company defaults/preferences, presentation feature toggles, locale, timezone, date-format and currency-format requests.

## Authority boundary

The Framework creates immutable tenant-bound requests and delegates configuration persistence and enforcement to authoritative Core/application services. It does not create a second configuration store or security authority.

Security-sensitive platform configuration, licensing, authentication, authorization and Core infrastructure settings remain outside this Company Platform boundary.

## Tenant isolation

Every request is bound to the authenticated organisation and cross-tenant requests are rejected before delegation.

## Presentation features

Presentation feature keys describe UI/application presentation controls only. A feature toggle does not grant permissions, entitlements or access to a business capability.

## Testing

`tests/test_company_configuration_admin_cp024.py` covers tenant binding, immutability, required keys/values, feature-key validation, format values, cross-tenant rejection, delegation and authentication enforcement.

Tests were added but were not executed in the available GitHub-only environment.
