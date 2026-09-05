import pytest

from phoenix_framework.external_modules import bundle_from_manifest, register_external_manifest
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


def crm_manifest():
    return {
        "module": {
            "code": "crm",
            "name": "CRM",
            "version": "1.0.0",
            "description": "Phoenix CRM 360 V1.0",
            "required_permissions": ("crm.view",),
            "required_entitlements": ("crm",),
            "navigation_keys": ("crm.workspace",),
            "capabilities": ("crm.customer_context",),
        },
        "integration": {
            "module_code": "crm",
            "version": "1.0.0",
            "provided_contracts": ("crm.customer.v1", "crm.contact.v1"),
            "provided_capabilities": ("crm.customer_context",),
        },
        "navigation": (
            {
                "key": "crm.workspace",
                "label": "CRM",
                "route": "/modules/crm",
                "module_code": "crm",
                "permission": "crm.view",
                "entitlement": "crm",
            },
        ),
    }


def test_crm_manifest_converts_to_core_contracts_without_business_imports():
    bundle = bundle_from_manifest(crm_manifest())

    assert bundle.module.code == "crm"
    assert bundle.module.version == "1.0.0"
    assert bundle.integration.provides_contract("crm.customer.v1")
    assert bundle.integration.provides_capability("crm.customer_context")
    assert bundle.navigation[0].key == "crm.workspace"


def test_crm_manifest_registers_atomically():
    modules = ModuleRegistry()
    navigation = NavigationRegistry()

    register_external_manifest(crm_manifest(), modules, navigation)

    assert modules.has("crm")
    assert navigation.has("crm.workspace")


def test_manifest_rejects_non_mapping_module_data_before_registration():
    manifest = crm_manifest()
    manifest["module"] = "crm"
    modules = ModuleRegistry()
    navigation = NavigationRegistry()

    with pytest.raises(ValueError, match="module and integration mappings"):
        register_external_manifest(manifest, modules, navigation)

    assert modules.list() == []
    assert navigation.list() == []


def test_manifest_rejects_blank_sequence_values():
    manifest = crm_manifest()
    manifest["module"] = dict(manifest["module"])
    manifest["module"]["capabilities"] = ("crm.customer_context", " ")

    with pytest.raises(ValueError, match="capabilities cannot contain blank values"):
        bundle_from_manifest(manifest)
