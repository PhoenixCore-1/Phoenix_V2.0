from pathlib import Path
import sqlite3

import pytest

from phoenix_core.modules.account_360_runtime import Account360Runtime, Account360RuntimeError
from phoenix_core.modules.service import ModuleService


SCHEMA = """
CREATE TABLE modules (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def _service():
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db, ModuleService(db)


def _write_package(root: Path, *, code="account_360", name="Account 360", version="1.0.0"):
    package = root / "account_360"
    package.mkdir()
    (package / "__init__.py").write_text(
        f'__module_code__ = "{code}"\n'
        f'__module_name__ = "{name}"\n'
        f'__version__ = "{version}"\n',
        encoding="utf-8",
    )


def test_verify_package_uses_explicit_external_path(tmp_path):
    _write_package(tmp_path)
    _, service = _service()
    loaded = Account360Runtime(service).verify_package(tmp_path)
    assert loaded.code == "account_360"
    assert loaded.name == "Account 360"
    assert loaded.version == "1.0.0"
    assert loaded.package == "account_360"


def test_missing_package_is_rejected(tmp_path):
    _, service = _service()
    with pytest.raises(Account360RuntimeError, match="unavailable"):
        Account360Runtime(service).verify_package(tmp_path)


def test_metadata_mismatch_is_rejected(tmp_path):
    _write_package(tmp_path, version="9.9.9")
    _, service = _service()
    with pytest.raises(Account360RuntimeError, match="metadata"):
        Account360Runtime(service).verify_package(tmp_path)


def test_register_persists_core_registry_metadata(tmp_path):
    _write_package(tmp_path)
    db, service = _service()
    module = Account360Runtime(service).register(tmp_path)
    row = db.execute("SELECT code,name,version,status FROM modules").fetchone()
    assert module.code == "account_360"
    assert tuple(row) == ("account_360", "Account 360", "1.0.0", "REGISTERED")


def test_enable_uses_core_lifecycle_service(tmp_path):
    _write_package(tmp_path)
    _, service = _service()
    runtime = Account360Runtime(service)
    runtime.register(tmp_path)
    module = runtime.enable(tmp_path)
    assert module.status == "ENABLED"


def test_disable_uses_core_lifecycle_service(tmp_path):
    _write_package(tmp_path)
    _, service = _service()
    runtime = Account360Runtime(service)
    runtime.register(tmp_path)
    runtime.enable(tmp_path)
    module = runtime.disable()
    assert module.status == "DISABLED"


def test_duplicate_registration_is_rejected_by_core_registry(tmp_path):
    _write_package(tmp_path)
    _, service = _service()
    runtime = Account360Runtime(service)
    runtime.register(tmp_path)
    with pytest.raises(Account360RuntimeError, match="registration failed"):
        runtime.register(tmp_path)
