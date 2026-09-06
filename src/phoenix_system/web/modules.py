"""System-level registration of Phoenix business module descriptors.

The System shell consumes the Generic Framework module registry. It does not
own business logic, licensing or authorization decisions; those remain
Phoenix Core responsibilities.
"""

from phoenix_framework.contracts import ModuleContract, ModuleLifecycle
from phoenix_framework.modules.registry import ModuleRegistry


SYSTEM_MODULE_DEFINITIONS = (
    ModuleContract(
        code="crm",
        name="CRM 360",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Customer relationships, activities and customer intelligence.",
        navigation_keys=("crm.dashboard",),
    ),
    ModuleContract(
        code="sales",
        name="Sales 360",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Opportunities, quotes, pricing and orders.",
        navigation_keys=("sales.dashboard",),
    ),
    ModuleContract(
        code="inventory",
        name="Inventory 360",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Physical stock, warehouse and inventory operations.",
        navigation_keys=("inventory.dashboard",),
    ),
    ModuleContract(
        code="manufacturing",
        name="Manufacturing",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Manufacturing orders, stages, quantities and production control.",
        navigation_keys=("manufacturing.dashboard",),
        metadata={"module_code": "production"},
    ),
    ModuleContract(
        code="procurement",
        name="Procurement",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Purchasing, suppliers and demand-driven procurement.",
        navigation_keys=("procurement.dashboard",),
    ),
    ModuleContract(
        code="projects",
        name="Projects",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Projects, activities, requirements and progress.",
        navigation_keys=("projects.dashboard",),
    ),
    ModuleContract(
        code="accounts",
        name="Accounts",
        version="1.0.0",
        lifecycle=ModuleLifecycle.ENABLED,
        description="Financial visibility and accounting integration.",
        navigation_keys=("accounts.dashboard",),
    ),
)


def register_system_modules(registry: ModuleRegistry) -> None:
    """Register framework descriptors for modules known to the System shell."""
    for module in SYSTEM_MODULE_DEFINITIONS:
        if not registry.has(module.code):
            registry.register(module)


def enabled_modules(registry: ModuleRegistry) -> list[ModuleContract]:
    """Return enabled module descriptors for presentation."""
    return [module for module in registry.list() if module.enabled]
