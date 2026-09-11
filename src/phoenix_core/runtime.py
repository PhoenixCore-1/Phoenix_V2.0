"""Phoenix Core V2 runtime composition root.

This module is the single supported construction boundary for the first
runtime slice.  It wires infrastructure, the Core foundation service,
CoreApi, and the integration service without exposing database access to
clients or modules.
"""

from dataclasses import dataclass
from pathlib import Path

from phoenix_core.api.application import CoreApi
from phoenix_core.api.integration.service import CoreIntegrationService
from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.services import CoreFoundationService


@dataclass
class CoreRuntime:
    """Live V2 Core runtime and its authoritative application boundaries."""

    db: SQLiteDatabase
    service: CoreFoundationService
    api: CoreApi
    integration: CoreIntegrationService

    def close(self) -> None:
        """Close the runtime database connection."""
        self.db.close()


def build_runtime(
    database_path: str | Path,
    *,
    initialise: bool = True,
    realtime_publisher=None,
) -> CoreRuntime:
    """Construct the authoritative Phoenix Core V2 runtime.

    The composition order is intentionally explicit:

        SQLiteDatabase -> CoreFoundationService -> CoreApi
        -> CoreIntegrationService

    ``initialise`` applies the Core foundation migrations through the
    service-owned initialisation path.  Callers that manage migrations
    separately may disable it.
    """

    db = SQLiteDatabase(database_path)
    service = CoreFoundationService(
        db,
        realtime_publisher=realtime_publisher,
    )

    try:
        if initialise:
            service.initialise()

        api = CoreApi(db, service)
        integration = CoreIntegrationService(api)
        return CoreRuntime(
            db=db,
            service=service,
            api=api,
            integration=integration,
        )
    except Exception:
        db.close()
        raise
