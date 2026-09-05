from uuid import uuid4

from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleLifecycle
from phoenix_framework.contracts.invocation import ModuleInvocationRequest
from phoenix_framework.integration.registry import IntegrationRegistry
from phoenix_framework.integration.runtime import ModuleInvocationRuntime
from phoenix_framework.integration.service import ModuleInvocationService
from phoenix_framework.modules import ModuleRegistry


def _context():
    return FrameworkContext(
        request_id="req-runtime",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset({"crm.view"}),
        entitlements=frozenset({"crm"}),
    )


def _runtime(handler):
    modules = ModuleRegistry()
    modules.register(ModuleContract(code="sales", name="Sales", version="1.0.0", lifecycle=ModuleLifecycle.ENABLED))
    modules.register(ModuleContract(code="crm", name="CRM", version="1.0.0", lifecycle=ModuleLifecycle.ENABLED))
    integrations = IntegrationRegistry()
    integrations.register("crm", "crm.customer.v1", handler)
    return ModuleInvocationRuntime(ModuleInvocationService(modules, integrations))


def _request():
    return ModuleInvocationRequest(
        request_id="req-runtime",
        source_module="sales",
        target_module="crm",
        contract="crm.customer.v1",
        operation="get_customer",
        context=_context(),
        payload={"customer_id": "customer-1"},
    )


def test_runtime_invokes_published_capability():
    runtime = _runtime(lambda **kwargs: {"customer_id": kwargs["payload"]["customer_id"]})
    response = runtime.invoke(_request())
    assert response.success is True
    assert response.data == {"customer_id": "customer-1"}


def test_runtime_normalizes_boundary_failure():
    runtime = _runtime(lambda **kwargs: {"ok": True})
    request = ModuleInvocationRequest(
        request_id="req-runtime",
        source_module="sales",
        target_module="crm",
        contract="crm.customer.v1",
        operation="get_customer",
        context=_context(),
        payload={"customer_id": "customer-1"},
    )
    runtime._service.module_registry.get("crm").required_permissions = ("crm.admin",)
