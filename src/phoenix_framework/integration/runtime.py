"""High-level runtime boundary for Phoenix module capabilities."""

from __future__ import annotations

from phoenix_framework.contracts.invocation import (
    ModuleInvocationRequest,
    ModuleInvocationResponse,
)
from phoenix_framework.integration.service import ModuleInvocationService


class ModuleInvocationRuntime:
    """Small composition boundary used by a Phoenix host application.

    Modules remain unaware of the Core implementation. The host supplies the
    Core-owned invocation service and modules interact with this boundary via
    published invocation requests only.
    """

    def __init__(self, service: ModuleInvocationService) -> None:
        self._service = service

    def invoke(self, request: ModuleInvocationRequest) -> ModuleInvocationResponse:
        """Invoke a published module operation through Core."""
        return self._service.invoke(request)

    def invoke_safe(self, request: ModuleInvocationRequest) -> ModuleInvocationResponse:
        """Return a normalized failure response instead of leaking boundary errors."""
        try:
            return self.invoke(request)
        except (PermissionError, ValueError) as exc:
            return ModuleInvocationResponse(
                request_id=request.request_id,
                success=False,
                error=str(exc),
            )
