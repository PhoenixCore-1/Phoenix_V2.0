"""Phoenix Core V2 registration contract for Account 360.

The Account 360 package remains an independently deployed module. Core stores
only its registration metadata and lifecycle state; Account 360 business data
and rules remain outside Core.
"""

from dataclasses import dataclass


ACCOUNT_360_CODE = "account_360"
ACCOUNT_360_NAME = "Account 360"
ACCOUNT_360_VERSION = "1.0.0"
ACCOUNT_360_ROUTE = "/account-360"


@dataclass(frozen=True)
class Account360Registration:
    code: str = ACCOUNT_360_CODE
    name: str = ACCOUNT_360_NAME
    version: str = ACCOUNT_360_VERSION
    route: str = ACCOUNT_360_ROUTE
    default_enabled: bool = False
    external_package: str = "account_360"


REGISTRATION = Account360Registration()


def registration() -> Account360Registration:
    return REGISTRATION
