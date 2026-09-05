from uuid import uuid4

from phoenix_framework.capabilities.discovery import discover_capabilities
from phoenix_framework.capabilities.registry import CapabilityRegistry
from phoenix_framework.context import FrameworkContext
from phoenix_framework.contracts import PlatformCapability
from phoenix_framework.contracts.capability import PlatformCapabilityContract


class TestCapability(PlatformCapabilityContract):
    def __init__(self, *, enabled=True, permissions=(), entitlements=(), available=True):
        self._capability = PlatformCapability(
            code="sales.quotes",
            name="Sales Quotes",
            description="Quote capability",
            enabled=enabled,
        )
        self._permissions = permissions
        self._entitlements = entitlements
        self._available = available

    @property
    def capability(self):
        return self._capability

    def is_available(self, context):
        return self._available

    def required_permissions(self):
        return self._permissions

    def required_entitlements(self):
        return self._entitlements


def context(*, permissions=(), entitlements=()):
    return FrameworkContext(
        request_id="request-1",
        identity_id=uuid4(),
        organisation_id=uuid4(),
        session_id=uuid4(),
        permissions=frozenset(permissions),
        entitlements=frozenset(entitlements),
    )


def test_capability_requires_core_permission_and_entitlement():
    registry = CapabilityRegistry()
    registry.register(
        TestCapability(
            permissions=("sales.quote.read",),
            entitlements=("sales",),
        )
    )

    assert discover_capabilities(registry, context()) == []
    assert discover_capabilities(registry, context(entitlements=("sales",))) == []
    assert len(
        discover_capabilities(
            registry,
            context(permissions=("sales.quote.read",), entitlements=("sales",)),
        )
    ) == 1


def test_disabled_or_unavailable_capability_is_hidden():
    registry = CapabilityRegistry()
    registry.register(TestCapability(enabled=False))
    assert discover_capabilities(registry, context()) == []

    registry.clear()
    registry.register(TestCapability(available=False))
    assert discover_capabilities(registry, context()) == []
