"""Phoenix Core V2 licensing boundary for Account 360.

Core owns organisation/module entitlement decisions. Account 360 consumes this
capability and does not implement licensing or entitlement rules itself.
"""

from uuid import UUID

from phoenix_core.licensing.service import EntitlementService
from phoenix_core.modules.account_360 import ACCOUNT_360_CODE
from phoenix_core.modules.service import ModuleService


class Account360LicensingError(RuntimeError):
    """Raised when the Account 360 entitlement boundary cannot be evaluated."""


class Account360Licensing:
    """Resolve Account 360 availability through Core's authoritative services."""

    def __init__(
        self,
        module_service: ModuleService,
        entitlement_service: EntitlementService,
    ):
        self.module_service = module_service
        self.entitlement_service = entitlement_service

    def module_id(self) -> UUID:
        """Return the registered Core module id for Account 360."""
        try:
            return self.module_service.get_by_code(ACCOUNT_360_CODE).id
        except Exception as exc:
            raise Account360LicensingError(
                "Account 360 is not registered in Core."
            ) from exc

    def is_available(self, organisation_id: UUID) -> bool:
        """Return whether an organisation may use Account 360 right now."""
        if not organisation_id:
            return False
        try:
            return self.entitlement_service.is_module_available(
                organisation_id,
                self.module_id(),
            )
        except Exception as exc:
            raise Account360LicensingError(
                "Unable to evaluate the Account 360 entitlement."
            ) from exc

    def require_available(self, organisation_id: UUID) -> None:
        """Fail closed unless Account 360 is currently licensed and enabled."""
        if not self.is_available(organisation_id):
            raise Account360LicensingError(
                "Account 360 is not licensed or enabled for this organisation."
            )
