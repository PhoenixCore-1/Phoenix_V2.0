from pathlib import Path
from uuid import uuid4

import pytest

from phoenix_core.errors import AuthorizationError, ConflictError, NotFoundError
from phoenix_core.licensing.service import EntitlementService
from phoenix_core.modules.account_360 import ACCOUNT_360_CODE, ACCOUNT_360_NAME, ACCOUNT_360_VERSION
from phoenix_core.modules.account_360_licensing import Account360Licensing, Account360LicensingError
from phoenix_core.modules.service import ModuleService


SCHEMA = """
CREATE TABLE organisations (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL
);
CREATE TABLE modules (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE module_entitlements (
    id TEXT PRIMARY KEY,
    organisation_id TEXT NOT NULL,
    module_id TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(organisation_id, module_id)
);
"""


def db():
    import sqlite3
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def setup():
    connection = db()
    module_service = ModuleService(connection)
    entitlement_service = EntitlementService(connection)
    module = module_service.register(
        ACCOUNT_360_CODE,
        ACCOUNT_360_NAME,
        ACCOUNT_360_VERSION,
    )
    organisation_id = uuid4()
    connection.execute(
        "INSERT INTO organisations(id,status) VALUES (?,?)",
        (str(organisation_id), "ACTIVE"),
    )
    connection.commit()
    return connection, module_service, entitlement_service, module, organisation_id


def test_unlicensed_account_360_is_unavailable():
    _, module_service, entitlement_service, _, organisation_id = setup()
    licensing = Account360Licensing(module_service, entitlement_service)

    assert licensing.is_available(organisation_id) is False
    with pytest.raises(Account360LicensingError):
        licensing.require_available(organisation_id)


def test_active_entitlement_requires_enabled_module():
    connection, module_service, entitlement_service, module, organisation_id = setup()
    entitlement_service.grant(organisation_id, module.id)
    licensing = Account360Licensing(module_service, entitlement_service)

    assert licensing.is_available(organisation_id) is False
    module_service.enable(module.id)
    assert licensing.is_available(organisation_id) is True
    licensing.require_available(organisation_id)
    connection.close()


def test_suspended_entitlement_blocks_access():
    connection, module_service, entitlement_service, module, organisation_id = setup()
    entitlement = entitlement_service.grant(organisation_id, module.id)
    module_service.enable(module.id)
    entitlement_service.suspend(entitlement.id)
    licensing = Account360Licensing(module_service, entitlement_service)

    assert licensing.is_available(organisation_id) is False
    with pytest.raises(Account360LicensingError):
        licensing.require_available(organisation_id)
    connection.close()


def test_revoked_entitlement_cannot_be_reactivated():
    connection, module_service, entitlement_service, module, organisation_id = setup()
    entitlement = entitlement_service.grant(organisation_id, module.id)
    entitlement_service.revoke(entitlement.id)

    with pytest.raises(Exception):
        entitlement_service.activate(entitlement.id)
    connection.close()


def test_missing_registration_fails_closed():
    connection = db()
    module_service = ModuleService(connection)
    entitlement_service = EntitlementService(connection)
    licensing = Account360Licensing(module_service, entitlement_service)

    with pytest.raises(Account360LicensingError):
        licensing.module_id()
    with pytest.raises(Account360LicensingError):
        licensing.is_available(uuid4())
    connection.close()


def test_inactive_organisation_is_not_available():
    connection, module_service, entitlement_service, module, organisation_id = setup()
    connection.execute("UPDATE organisations SET status='SUSPENDED' WHERE id=?", (str(organisation_id),))
    connection.commit()
    entitlement_service.grant
    with pytest.raises(AuthorizationError):
        entitlement_service.grant(organisation_id, module.id)
    connection.close()
