"""Phoenix Core V2 runtime boundary for the external Account 360 module.

Core owns registration and lifecycle state. The Account 360 package remains
external and owns its business rules and data.
"""

from dataclasses import dataclass
from pathlib import Path

from phoenix_core.errors import ValidationError
from phoenix_core.modules.account_360 import (
    ACCOUNT_360_CODE,
    ACCOUNT_360_NAME,
    ACCOUNT_360_VERSION,
    Account360Registration,
)
from phoenix_core.modules.service import ModuleService


class Account360RuntimeError(RuntimeError):
    """Raised when the external Account 360 runtime cannot be verified."""


@dataclass(frozen=True)
class LoadedAccount360:
    code: str
    name: str
    version: str
    package: str
    registration: Account360Registration


class Account360Runtime:
    """Verify and manage the external Account 360 module runtime."""

    PACKAGE = "account_360"

    def __init__(self, module_service: ModuleService):
        self.module_service = module_service

    def verify_package(self, module_path: str | Path) -> LoadedAccount360:
        path = Path(module_path).expanduser().resolve()
        if not path.exists() or not path.is_dir():
            raise Account360RuntimeError(f"Account 360 module path is unavailable: {path}")

        import sys
        import importlib

        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

        try:
            module = importlib.import_module(self.PACKAGE)
        except ImportError as exc:
            raise Account360RuntimeError("Unable to load external Account 360 package.") from exc

        code = str(getattr(module, "__module_code__", ""))
        name = str(getattr(module, "__module_name__", ""))
        version = str(getattr(module, "__version__", ""))

        if (code, name, version) != (ACCOUNT_360_CODE, ACCOUNT_360_NAME, ACCOUNT_360_VERSION):
            raise Account360RuntimeError(
                "Account 360 package metadata does not match the Core V2 contract."
            )

        return LoadedAccount360(
            code=code,
            name=name,
            version=version,
            package=self.PACKAGE,
            registration=Account360Registration(),
        )

    def register(self, module_path: str | Path):
        loaded = self.verify_package(module_path)
        try:
            return self.module_service.register(
                loaded.code,
                loaded.name,
                loaded.version,
            )
        except Exception as exc:
            raise Account360RuntimeError("Account 360 registration failed.") from exc

    def enable(self, module_path: str | Path):
        loaded = self.verify_package(module_path)
        module = self.module_service.get_by_code(loaded.code)
        return self.module_service.enable(module.id)

    def disable(self):
        module = self.module_service.get_by_code(ACCOUNT_360_CODE)
        return self.module_service.disable(module.id)
