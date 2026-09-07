from phoenix_core.modules.account_360 import (
    ACCOUNT_360_CODE,
    ACCOUNT_360_NAME,
    ACCOUNT_360_ROUTE,
    ACCOUNT_360_VERSION,
    registration,
)
from phoenix_core.modules.domain import Module


def test_account_360_registration_is_not_core_owned():
    reg = registration()
    assert reg.code == ACCOUNT_360_CODE
    assert reg.name == ACCOUNT_360_NAME
    assert reg.version == ACCOUNT_360_VERSION
    assert reg.route == ACCOUNT_360_ROUTE
    assert reg.default_enabled is False
    assert reg.external_package == "account_360"


def test_account_360_registration_is_valid_module_metadata():
    module = Module.create(ACCOUNT_360_CODE, ACCOUNT_360_NAME, ACCOUNT_360_VERSION)
    assert module.code == ACCOUNT_360_CODE
    assert module.name == ACCOUNT_360_NAME
    assert module.version == ACCOUNT_360_VERSION
    assert module.status == "REGISTERED"
