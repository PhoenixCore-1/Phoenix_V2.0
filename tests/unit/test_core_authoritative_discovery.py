from uuid import uuid4

from phoenix_framework.context.framework import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleLifecycle, NavigationContract
from phoenix_framework.discovery import discover_modules, discover_navigation
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


def _context(*, entitlements=(), permissions=()):
    return FrameworkContext(
        request_id="request-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(permissions),
        entitlements=frozenset(entitlements),
    )


def _sales_module():
    return ModuleContract(
        code="sales",
        name="Sales",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        required_entitlements=("sales",),
        navigation_keys=("sales.workspace",),
    )


def test_enabled_module_is_discoverable_when_core_context_has_entitlement():
    registry = ModuleRegistry()
    registry.register(_sales_module())

    discovered = discover_modules(registry, _context(entitlements=("sales",)))

    assert [module.code for module in discovered] == ["sales"]


def test_module_is_not_discoverable_without_core_entitlement():
    registry = ModuleRegistry()
    registry.register(_sales_module())

    discovered = discover_modules(registry, _context())

    assert discovered == []


def test_navigation_requires_core_entitlement_and_permission():
    registry = NavigationRegistry()
    registry.register(
        NavigationContract(
            key="sales.workspace",
            label="Sales",
            route="/modules/sales",
            module_code="sales",
            entitlement="sales",
            permission="sales.view",
        )
    )

    assert discover_navigation(registry, _context()) == []
    assert discover_navigation(registry, _context(entitlements=("sales",))) == []
    assert len(
        discover_navigation(
            registry,
            _context(entitlements=("sales",), permissions=("sales.view",)),
        )
    ) == 1


def test_disabled_module_is_not_discoverable_even_with_entitlement():
    registry = ModuleRegistry()
    registry.register(
        ModuleContract(
            code="sales",
            name="Sales",
            version="1.0.0",
            lifecycle=ModuleLifecycle.DISABLED,
            required_entitlements=("sales",),
        )
    )

    assert discover_modules(registry, _context(entitlements=("sales",))) == []
