from phoenix_framework.contracts import ModuleContract, ModuleIntegrationContract, NavigationContract
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry
from phoenix_framework.registration import ModuleRegistrationBundle, register_module


def bundle(code="sales", version="1.0.0"):
    module = ModuleContract(code=code, name=code.title(), version=version)
    integration = ModuleIntegrationContract(module_code=code, version=version)
    navigation = NavigationContract(
        key=f"{code}.workspace",
        label=code.title(),
        route=f"/modules/{code}",
        module_code=code,
        entitlement=code,
    )
    return ModuleRegistrationBundle(module=module, integration=integration, navigation=(navigation,))


def test_external_module_registers_into_core_framework_registries():
    modules = ModuleRegistry()
    navigation = NavigationRegistry()

    register_module(bundle(), modules, navigation)

    assert modules.has("sales")
    assert modules.get("sales").version == "1.0.0"
    assert navigation.has("sales.workspace")
    assert navigation.get("sales.workspace").entitlement == "sales"


def test_registration_rejects_module_integration_mismatch():
    modules = ModuleRegistry()
    navigation = NavigationRegistry()
    value = bundle()
    bad = ModuleRegistrationBundle(
        module=value.module,
        integration=ModuleIntegrationContract(module_code="sales", version="2.0.0"),
        navigation=value.navigation,
    )

    try:
        register_module(bad, modules, navigation)
        assert False, "expected version mismatch"
    except ValueError as exc:
        assert "versions" in str(exc)

    assert not modules.has("sales")
    assert not navigation.has("sales.workspace")


def test_registration_rejects_duplicate_module_without_mutation():
    modules = ModuleRegistry()
    navigation = NavigationRegistry()
    register_module(bundle(), modules, navigation)

    try:
        register_module(bundle(), modules, navigation)
        assert False, "expected duplicate module"
    except ValueError as exc:
        assert "already registered" in str(exc)

    assert len(modules.list()) == 1
    assert len(navigation.list()) == 1
