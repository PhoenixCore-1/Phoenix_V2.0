from uuid import uuid4

from phoenix_framework.capabilities.registry import CapabilityRegistry
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleIntegrationContract, ModuleLifecycle
from phoenix_framework.contracts.integration import ModuleDependency
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry
from phoenix_framework.workspace import discover_module_workspaces


def context():
    return FrameworkContext(
        request_id="request-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(),
        entitlements=frozenset(("sales",)),
    )


def module(code, entitlement=()):
    return ModuleContract(
        code=code,
        name=code.title(),
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        required_entitlements=entitlement,
    )


def test_required_dependency_blocks_workspace_when_missing():
    modules = ModuleRegistry()
    modules.register(module("sales", ("sales",)))

    sales_contract = ModuleIntegrationContract(
        module_code="sales",
        version="1.0.0",
        dependencies=(ModuleDependency("crm"),),
    )

    workspaces = discover_module_workspaces(
        modules,
        NavigationRegistry(),
        CapabilityRegistry(),
        context(),
        (sales_contract,),
    )

    assert workspaces == []


def test_optional_missing_dependency_does_not_block_workspace():
    modules = ModuleRegistry()
    modules.register(module("sales", ("sales",)))

    sales_contract = ModuleIntegrationContract(
        module_code="sales",
        version="1.0.0",
        dependencies=(ModuleDependency("crm", required=False),),
    )

    workspaces = discover_module_workspaces(
        modules,
        NavigationRegistry(),
        CapabilityRegistry(),
        context(),
        (sales_contract,),
    )

    assert [workspace.module.code for workspace in workspaces] == ["sales"]


def test_compatible_required_dependency_allows_workspace():
    modules = ModuleRegistry()
    modules.register(module("sales", ("sales",)))
    modules.register(module("crm"))

    sales_contract = ModuleIntegrationContract(
        module_code="sales",
        version="1.0.0",
        dependencies=(ModuleDependency("crm", minimum_version="1.0.0"),),
    )
    crm_contract = ModuleIntegrationContract(module_code="crm", version="1.0.0")

    workspaces = discover_module_workspaces(
        modules,
        NavigationRegistry(),
        CapabilityRegistry(),
        context(),
        (sales_contract, crm_contract),
    )

    assert [workspace.module.code for workspace in workspaces] == ["crm", "sales"]
