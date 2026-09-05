from uuid import uuid4

from phoenix_framework.capabilities.registry import CapabilityRegistry
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleLifecycle, NavigationContract, PlatformCapability
from phoenix_framework.contracts.capability import PlatformCapabilityContract
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry
from phoenix_framework.workspace import discover_module_workspaces


class SalesQuotesCapability(PlatformCapabilityContract):
    @property
    def capability(self):
        return PlatformCapability("sales.quotes", "Sales Quotes", "Quote capability")

    def is_available(self, context):
        return True

    def required_permissions(self):
        return ()

    def required_entitlements(self):
        return ("sales",)


def context(*, entitlements=()):
    return FrameworkContext(
        request_id="request-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(entitlements),
    )


def test_workspace_contains_only_authorized_module_navigation_and_capabilities():
    modules = ModuleRegistry()
    modules.register(
        ModuleContract(
            code="sales",
            name="Sales",
            version="1.0.0",
            lifecycle=ModuleLifecycle.ENABLED,
            required_entitlements=("sales",),
            navigation_keys=("sales.workspace",),
            capabilities=("sales.quotes", "sales.orders"),
        )
    )

    navigation = NavigationRegistry()
    navigation.register(
        NavigationContract(
            key="sales.workspace",
            label="Sales",
            route="/modules/sales",
            module_code="sales",
            entitlement="sales",
        )
    )

    capabilities = CapabilityRegistry()
    capabilities.register(SalesQuotesCapability())

    assert discover_module_workspaces(
        modules, navigation, capabilities, context()
    ) == []

    workspaces = discover_module_workspaces(
        modules, navigation, capabilities, context(entitlements=("sales",))
    )

    assert len(workspaces) == 1
    assert workspaces[0].module.code == "sales"
    assert [item.key for item in workspaces[0].navigation] == ["sales.workspace"]
    assert workspaces[0].capabilities == ("sales.quotes",)
