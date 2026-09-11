"""Bootstrap explicit Phoenix Core V2 demo accounts for controlled testing.

This is intentionally an operator-invoked script. It is NOT part of runtime
initialisation and never creates known credentials automatically.

Usage:
    PHOENIX_CORE_V2_DATABASE=/path/to/phoenix.db \
    PHOENIX_DEMO_PASSWORD='use-a-strong-temporary-password' \
    python scripts/bootstrap_demo_users.py

Accounts created/updated:
    system.admin  -> Phoenix System Platform
    company.admin -> Phoenix Company Platform
    user.demo     -> Phoenix User Platform

All three accounts use the same active demo organisation. The password is
supplied by the operator and is never stored in this source file.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phoenix_core.infrastructure import SQLiteDatabase
from phoenix_core.security.passwords import hash_password

ORG_CODE = "PHOENIX-DEMO"
ORG_NAME = "Phoenix Demo Organisation"
ACCOUNTS = (
    ("system.admin", "Phoenix System Administrator", "platform.system.access"),
    ("company.admin", "Phoenix Company Administrator", "platform.company.access"),
    ("user.demo", "Phoenix User", None),
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_permission(db, code: str) -> str:
    row = db.execute("SELECT id FROM permissions WHERE code=?", (code,)).fetchone()
    if row:
        return row["id"]
    permission_id = str(uuid4())
    db.execute(
        "INSERT INTO permissions(id,code,name,created_at) VALUES (?,?,?,?)",
        (permission_id, code, code, now()),
    )
    return permission_id


def ensure_role(db, organisation_id: str, code: str, name: str) -> str:
    row = db.execute(
        "SELECT id FROM roles WHERE organisation_id=? AND code=?",
        (organisation_id, code),
    ).fetchone()
    if row:
        return row["id"]
    role_id = str(uuid4())
    db.execute(
        "INSERT INTO roles(id,organisation_id,code,name,scope,status,created_at) VALUES (?,?,?,?,?,?,?)",
        (role_id, organisation_id, code, name, "ORGANISATION", "ACTIVE", now()),
    )
    return role_id


def ensure_user(db, username: str, display_name: str, password: str) -> tuple[str, str]:
    row = db.execute(
        "SELECT id, identity_id FROM users WHERE username=?", (username,)
    ).fetchone()
    password_hash = hash_password(password)
    if row:
        db.execute(
            "UPDATE users SET display_name=?, password_hash=?, status='ACTIVE' WHERE id=?",
            (display_name, password_hash, row["id"]),
        )
        db.execute(
            "UPDATE identities SET status='ACTIVE' WHERE id=?", (row["identity_id"],)
        )
        return row["id"], row["identity_id"]

    identity_id = str(uuid4())
    user_id = str(uuid4())
    timestamp = now()
    db.execute(
        "INSERT INTO identities(id,identity_type,status,created_at) VALUES (?,?,?,?)",
        (identity_id, "HUMAN", "ACTIVE", timestamp),
    )
    db.execute(
        "INSERT INTO users(id,identity_id,username,display_name,password_hash,status,created_at) VALUES (?,?,?,?,?,?,?)",
        (user_id, identity_id, username, display_name, password_hash, "ACTIVE", timestamp),
    )
    return user_id, identity_id


def ensure_membership(db, identity_id: str, organisation_id: str) -> str:
    row = db.execute(
        "SELECT id FROM organisation_memberships WHERE identity_id=? AND organisation_id=?",
        (identity_id, organisation_id),
    ).fetchone()
    if row:
        db.execute(
            "UPDATE organisation_memberships SET status='ACTIVE' WHERE id=?",
            (row["id"],),
        )
        return row["id"]
    membership_id = str(uuid4())
    db.execute(
        "INSERT INTO organisation_memberships(id,identity_id,organisation_id,status,created_at) VALUES (?,?,?,?,?)",
        (membership_id, identity_id, organisation_id, "ACTIVE", now()),
    )
    return membership_id


def ensure_role_assignment(db, membership_id: str, role_id: str) -> None:
    if db.execute(
        "SELECT 1 FROM role_assignments WHERE membership_id=? AND role_id=?",
        (membership_id, role_id),
    ).fetchone():
        return
    db.execute(
        "INSERT INTO role_assignments(id,membership_id,role_id,created_at) VALUES (?,?,?,?)",
        (str(uuid4()), membership_id, role_id, now()),
    )


def main() -> int:
    database_path = os.getenv("PHOENIX_CORE_V2_DATABASE")
    password = os.getenv("PHOENIX_DEMO_PASSWORD")
    if not database_path:
        print("PHOENIX_CORE_V2_DATABASE is required.", file=sys.stderr)
        return 2
    if not password or len(password) < 12:
        print("PHOENIX_DEMO_PASSWORD is required and must be at least 12 characters.", file=sys.stderr)
        return 2

    db = SQLiteDatabase(database_path)
    try:
        db.executescript((ROOT / "migrations" / "001_core_foundation.sql").read_text(encoding="utf-8"))
        org = db.execute("SELECT id FROM organisations WHERE code=?", (ORG_CODE,)).fetchone()
        if org:
            organisation_id = org["id"]
            db.execute("UPDATE organisations SET name=?, status='ACTIVE' WHERE id=?", (ORG_NAME, organisation_id))
        else:
            organisation_id = str(uuid4())
            db.execute(
                "INSERT INTO organisations(id,code,name,status,created_at) VALUES (?,?,?,?,?)",
                (organisation_id, ORG_CODE, ORG_NAME, "ACTIVE", now()),
            )

        permission_ids = {}
        for _, _, permission in ACCOUNTS:
            if permission:
                permission_ids[permission] = ensure_permission(db, permission)

        for username, display_name, permission in ACCOUNTS:
            _, identity_id = ensure_user(db, username, display_name, password)
            membership_id = ensure_membership(db, identity_id, organisation_id)
            if permission:
                role_code = "PHOENIX_SYSTEM_ADMIN" if permission == "platform.system.access" else "PHOENIX_COMPANY_ADMIN"
                role_name = "Phoenix System Administrator" if permission == "platform.system.access" else "Phoenix Company Administrator"
                role_id = ensure_role(db, organisation_id, role_code, role_name)
                ensure_role_assignment(db, membership_id, role_id)
                db.execute(
                    "INSERT OR IGNORE INTO role_permissions(role_id,permission_id,created_at) VALUES (?,?,?)",
                    (role_id, permission_ids[permission], now()),
                )

        db.commit()
        print(f"Demo accounts ready in {database_path}")
        print("  system.admin  -> SYSTEM_PLATFORM")
        print("  company.admin -> COMPANY_PLATFORM")
        print("  user.demo     -> USER_PLATFORM")
        print("Password supplied through PHOENIX_DEMO_PASSWORD; it is not printed.")
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
