from phoenix_framework.external_modules import bundle_from_manifest
from phoenix_framework.contracts import ModuleIntegrationContract
from phoenix_framework.integration.dependency import ModuleDependencyResolver


def test_sales_optional_crm_dependency_resolves_when_capability_is_published():
    sales = bundle_from_manifest(
        {
            "module": {"code": "sales", "name": "Sales", "version": "1.0.0"},
            "integration": {
                "module_code": "sales",
                "version": "1.0.0",
                "dependencies": (
                    {
                        "module_code": "crm",
                        "minimum_version": "1.0.0",
                        "required": False,
                        "capabilities": ("crm.customer_context",),
                    },
                ),
            },
        }
    )
    crm = ModuleIntegrationContract(
        module_code="crm",
        version="1.0.0",
        provided_capabilities=("crm.customer_context",),
    )

    result = ModuleDependencyResolver().resolve(sales.integration, crm)

    assert result.compatible is True
    assert result.required is False


def test_sales_optional_crm_dependency_does_not_make_crm_mandatory():
    sales = bundle_from_manifest(
        {
            "module": {"code": "sales", "name": "Sales", "version": "1.0.0"},
            "integration": {
                "module_code": "sales",
                "version": "1.0.0",
                "dependencies": (
                    {
                        "module_code": "crm",
                        "minimum_version": "1.0.0",
                        "required": False,
                        "capabilities": ("crm.customer_context",),
                    },
                ),
            },
        }
    )
    resolver = ModuleDependencyResolver()
    resolution = resolver.resolve(
        sales.integration,
        ModuleIntegrationContract(module_code="crm", version="1.0.0"),
    )

    assert resolution.compatible is False
    assert resolution.required is False
