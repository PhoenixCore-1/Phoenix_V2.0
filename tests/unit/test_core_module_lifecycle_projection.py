from datetime import datetime, timezone
from uuid import uuid4

import pytest

from phoenix_core.modules.domain import Module
from phoenix_framework.contracts import ModuleLifecycle
from phoenix_framework.lifecycle import framework_lifecycle, is_discoverable


def _module(status: str) -> Module:
    return Module(
        id=uuid4(),
        code="sales",
        name="Sales",
        version="1.0.0",
        status=status,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.parametrize(
    ("status", "lifecycle", "discoverable"),
    [
        ("REGISTERED", ModuleLifecycle.REGISTERED, False),
        ("ENABLED", ModuleLifecycle.ENABLED, True),
        ("DISABLED", ModuleLifecycle.DISABLED, False),
        ("RETIRED", ModuleLifecycle.DEPRECATED, False),
    ],
)
def test_core_lifecycle_is_projected_without_creating_framework_authority(
    status, lifecycle, discoverable
):
    module = _module(status)

    assert framework_lifecycle(module) == lifecycle
    assert is_discoverable(module) is discoverable


def test_unknown_core_status_fails_closed():
    with pytest.raises(ValueError, match="Unknown Core module status"):
        framework_lifecycle(_module("UNKNOWN"))
