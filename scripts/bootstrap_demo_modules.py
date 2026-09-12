"""Bootstrap the Phoenix Core V2 demo module registry and entitlements.

This is intentionally an operator-invoked script. It is NOT part of runtime
initialisation and does not grant modules to arbitrary organisations.

Usage:
    PHOENIX_CORE_V2_DATABASE=/path/to/phoenix.db \
    python scripts/bootstrap_demo_modules.py

Current demo configuration:
    Phoenix Demo Organisation -> Production module

The script is idempotent:
- registers Production when it is missing;
- enables it when it is registered but not yet enabled;
- grants an ACTIVE organisation entitlement when it is missing;
- re-activates an existing SUSPENDED entitlement;
- never silently re-activates a REVOKED entitlement.

No production database is stored in the repository.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.modules.service import ModuleService
from phoenix_core.licensing.service import EntitlementService

ORG_CODE = "PHOENIX-DEMO"
MODULE_CODE = "production"
MODULE_NAME = "Production"
MODULE_VERSION = "1.0.0"


def main() -> int:
    database_path = os.getenv("PHOENIX_CORE_V2_DATABASE")
    if not database_path:
        print("PHOENIX_CORE_V2_DATABASE is required.", file=sys.stderr)
        return 2

    db = SQLiteDatabase(database_path)
    module_service = ModuleService(db)
    entitlement_service = EntitlementService(db)

    try:
        db.executescript(
            (ROOT / "migrations" / "001_core_foundation.sql").read_text(
                encoding="utf-8"
            )
        )

        organisation = db.execute(
            "SELECT id, status FROM organisations WHERE code=?",
            (ORG_CODE,),
        ).fetchone()
        if not organisation:
            print(f"Organisation {ORG_CODE!r} was not found.", file=sys.stderr)
            return 3
        if organisation["status"] != "ACTIVE":
            print(f"Organisation {ORG_CODE!r} is not ACTIVE.", file=sys.stderr)
            return 3

        try:
            module = module_service.get_by_code(MODULE_CODE)
            print(
                f"Module exists: {module.code} {module.version} ({module.status})"
            )
        except Exception as exc:
            if "Module not found" not in str(exc):
                raise
            module = module_service.register(
                MODULE_CODE,
                MODULE_NAME,
                MODULE_VERSION,
            )
            print(
                f"Registered module: {module.code} {module.version} ({module.status})"
            )

        if module.status == "REGISTERED":
            module = module_service.enable(module.id)
            print(f"Enabled module: {module.code} ({module.status})")
        elif module.status == "DISABLED":
            module = module_service.enable(module.id)
            print(f"Re-enabled module: {module.code} ({module.status})")
        elif module.status == "RETIRED":
            print(
                "Production module is RETIRED and cannot receive a new entitlement.",
                file=sys.stderr,
            )
            return 4

        entitlement = db.execute(
            """
            SELECT id, status
            FROM module_entitlements
            WHERE organisation_id=? AND module_id=?
            """,
            (organisation["id"], str(module.id)),
        ).fetchone()

        if entitlement:
            entitlement_id = UUID(entitlement["id"])
            if entitlement["status"] == "REVOKED":
                print(
                    "Production entitlement is REVOKED; it will not be silently recreated.",
                    file=sys.stderr,
                )
                return 5
            if entitlement["status"] == "SUSPENDED":
                entitlement_service.activate(entitlement_id)
                print("Activated existing Production entitlement.")
            else:
                print("Production entitlement already ACTIVE.")
        else:
            entitlement_service.grant(
                UUID(organisation["id"]),
                module.id,
            )
            print("Granted ACTIVE Production entitlement to Phoenix Demo Organisation.")

        db.commit()
        print("Demo module configuration ready.")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
