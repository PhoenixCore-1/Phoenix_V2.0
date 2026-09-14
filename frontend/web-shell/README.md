# Phoenix Web Shell

The Phoenix Web Shell is the shared browser boundary for Phoenix Platform destinations.

## Authority

The shell does not authenticate users independently and does not decide platform access locally. It uses the Phoenix Core session and `/api/v1/platform/destination` response as the authoritative destination source.

## Destinations

- `/system` — System Platform
- `/company` — Company Platform
- `/user` — User Platform

Destination applications remain separate workspaces. The shell is responsible for the shared Phoenix navigation boundary, not business-module authorization.

## Current state

This package documents the shared-shell boundary while the platform applications are progressively brought under the common shell. It intentionally does not duplicate the approved System Platform implementation or create placeholder business screens.
