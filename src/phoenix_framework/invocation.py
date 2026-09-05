"""Generic synchronous inter-module invocation runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping

from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import ModuleContract, ModuleIntegrationContract
from phoenix_framework.contracts.invocation import ModuleInvocationRequest, ModuleInvocationResponse


Handler = Callable[[ModuleInvocationRequest], Any]


@dataclass(frozen=True)
class ContractProvider:
    module_code: str
    contract: str
    version: str
    operations: Mapping[str, Handler]


class ContractProviderRegistry:
    """Registry of published module contract providers."""

    def __init__(self) -> None:
        self._providers: Dict[tuple[str, str], ContractProvider] = {}

    def register(self, provider: ContractProvider) -> None:
        key = (provider.module_code, provider.contract)
        if key in self._providers:
            raise ValueError(f"Contract already registered: {provider.module_code}:{provider.contract}")
        if not provider.operations:
            raise ValueError("Contract provider must publish at least one operation")
        self._providers[key] = provider

    def get(self, module_code: str, contract: str) -> ContractProvider:
        try:
            return self._providers[(module_code, contract)]
        except KeyError as exc:
            raise LookupError(f"Contract not found: {module_code}:{contract}") from exc


class ModuleInvocationService:
    """Authorize and dispatch synchronous module contract invocations."""

    def __init__(
        self,
        providers: ContractProviderRegistry,
        modules: Mapping[str, ModuleContract],
        integrations: Mapping[str, ModuleIntegrationContract],
    ) -> None:
        self._providers = providers
        self._modules = modules
        self._integrations = integrations

    def invoke(self, request: ModuleInvocationRequest) -> ModuleInvocationResponse:
        try:
            request.context.require_authenticated()
            request.context.require_tenant()

            source = self._modules.get(request.source_module)
            target = self._modules.get(request.target_module)
            if source is None or target is None:
                return ModuleInvocationResponse(request.request_id, False, error="MODULE_UNAVAILABLE")
            if not source.enabled or not target.enabled:
                return ModuleInvocationResponse(request.request_id, False, error="MODULE_UNAVAILABLE")

            integration = self._integrations.get(request.target_module)
            if integration is None or request.contract not in integration.provided_contracts:
                return ModuleInvocationResponse(request.request_id, False, error="CONTRACT_NOT_FOUND")

            provider = self._providers.get(request.target_module, request.contract)
            if provider.version != integration.version:
                return ModuleInvocationResponse(request.request_id, False, error="CONTRACT_INCOMPATIBLE")

            handler = provider.operations.get(request.operation)
            if handler is None:
                return ModuleInvocationResponse(request.request_id, False, error="OPERATION_NOT_FOUND")

            return ModuleInvocationResponse(request.request_id, True, data=handler(request))
        except PermissionError as exc:
            return ModuleInvocationResponse(request.request_id, False, error="UNAUTHORIZED")
        except LookupError as exc:
            return ModuleInvocationResponse(request.request_id, False, error="CONTRACT_NOT_FOUND")
        except Exception as exc:
            return ModuleInvocationResponse(request.request_id, False, error="HANDLER_FAILED")
