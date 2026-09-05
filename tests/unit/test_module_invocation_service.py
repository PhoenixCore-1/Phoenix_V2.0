from uuid import uuid4

from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleIntegrationContract, ModuleLifecycle
from phoenix_framework.contracts.invocation import ModuleInvocationRequest
from phoenix_framework.invocation import ContractProvider, ContractProviderRegistry, ModuleInvocationService


def ctx():
    return FrameworkContext("r1", uuid4(), uuid4(), uuid4(), frozenset(), frozenset())


def mod(code):
    return ModuleContract(code, code.title(), "1.0.0", lifecycle=ModuleLifecycle.ENABLED)


def request(contract="crm.customer.v1", operation="get_customer"):
    return ModuleInvocationRequest("r1", "sales", "crm", contract, operation, ctx(), {"customer_id": "C1"})


def service():
    providers = ContractProviderRegistry()
    providers.register(ContractProvider("crm", "crm.customer.v1", "1.0.0", {"get_customer": lambda req: {"id": req.payload["customer_id"]}}))
    return ModuleInvocationService(
        providers,
        {"sales": mod("sales"), "crm": mod("crm")},
        {"crm": ModuleIntegrationContract("crm", "1.0.0", provided_contracts=("crm.customer.v1",))},
    )


def test_invocation_dispatches_published_operation():
    response = service().invoke(request())
    assert response.success
    assert response.data == {"id": "C1"}


def test_disabled_target_fails_closed():
    target = ModuleContract("crm", "Crm", "1.0.0", lifecycle=ModuleLifecycle.DISABLED)
    svc = ModuleInvocationService(
        ContractProviderRegistry(),
        {"sales": mod("sales"), "crm": target},
        {},
    )
    response = svc.invoke(request())
    assert not response.success
    assert response.error == "MODULE_UNAVAILABLE"


def test_unpublished_contract_fails():
    response = service().invoke(request("crm.other.v1"))
    assert not response.success
    assert response.error == "CONTRACT_NOT_FOUND"


def test_missing_authentication_fails():
    c = FrameworkContext("r1", None, uuid4(), uuid4(), frozenset(), frozenset())
    req = ModuleInvocationRequest("r1", "sales", "crm", "crm.customer.v1", "get_customer", c)
    response = service().invoke(req)
    assert not response.success
    assert response.error == "UNAUTHORIZED"
