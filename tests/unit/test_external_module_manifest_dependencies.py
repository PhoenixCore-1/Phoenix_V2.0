import pytest

from phoenix_framework.external_modules import bundle_from_manifest


def test_optional_crm_dependency_is_preserved_as_a_published_contract():
    manifest = {
        "module": {"code": "sales", "name": "Sales", "version": "1.0.0"},
        "integration": {
            "module_code": "sales",
            "version": "1.0.0",
            "provided_capabilities": ("sales.customer_commercial_context",),
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

    bundle = bundle_from_manifest(manifest)
    dependency = bundle.integration.dependencies[0]

    assert dependency.module_code == "crm"
    assert dependency.minimum_version == "1.0.0"
    assert dependency.required is False
    assert dependency.requires_capability("crm.customer_context")


def test_invalid_dependency_entry_is_rejected():
    manifest = {
        "module": {"code": "sales", "name": "Sales", "version": "1.0.0"},
        "integration": {
            "module_code": "sales",
            "version": "1.0.0",
            "dependencies": ("crm",),
        },
    }

    with pytest.raises(ValueError, match="dependency entries must be mappings"):
        bundle_from_manifest(manifest)
