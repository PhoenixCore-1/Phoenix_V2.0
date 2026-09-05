"""Dependency-free manifest boundary for externally supplied Phoenix modules."""

from __future__ import annotations

from typing import Mapping, Sequence

from phoenix_framework.contracts import (
    ModuleContract,
    ModuleIntegrationContract,
    NavigationContract,
)
from phoenix_framework.registration import ModuleRegistrationBundle, register_module
from phoenix_framework.modules.registry import ModuleRegistry
from phoenix_framework.navigation.registry import NavigationRegistry


def _strings(value: object, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{field_name} must be a sequence of strings")
    values = tuple(str(item).strip() for item in value)
    if any(not item for item in values):
        raise ValueError(f"{field_name} cannot contain blank values")
    return values


def _metadata(value: object, field_name: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{field_name} must be a mapping")
    return {str(key): str(item) for key, item in value.items()}


def bundle_from_manifest(manifest: Mapping[str, object]) -> ModuleRegistrationBundle:
    """Convert an external module's plain-data manifest into Core contracts."""
    if not isinstance(manifest, Mapping):
        raise ValueError("Module manifest must be a mapping")

    module_data = manifest.get("module")
    integration_data = manifest.get("integration")
    navigation_data = manifest.get("navigation", ())
    if not isinstance(module_data, Mapping) or not isinstance(integration_data, Mapping):
        raise ValueError("Module manifest requires module and integration mappings")
    if isinstance(navigation_data, (str, bytes)) or not isinstance(navigation_data, Sequence):
        raise ValueError("Module manifest navigation must be a sequence")

    module = ModuleContract(
        code=str(module_data.get("code", "")).strip(),
        name=str(module_data.get("name", "")).strip(),
        version=str(module_data.get("version", "")).strip(),
        description=str(module_data.get("description", "")),
        required_permissions=_strings(module_data.get("required_permissions"), "required_permissions"),
        required_entitlements=_strings(module_data.get("required_entitlements"), "required_entitlements"),
        navigation_keys=_strings(module_data.get("navigation_keys"), "navigation_keys"),
        capabilities=_strings(module_data.get("capabilities"), "capabilities"),
        metadata=_metadata(module_data.get("metadata"), "module.metadata"),
    )
    integration = ModuleIntegrationContract(
        module_code=str(integration_data.get("module_code", "")).strip(),
        version=str(integration_data.get("version", "")).strip(),
        provided_contracts=_strings(integration_data.get("provided_contracts"), "provided_contracts"),
        provided_capabilities=_strings(integration_data.get("provided_capabilities"), "provided_capabilities"),
        provided_events=_strings(integration_data.get("provided_events"), "provided_events"),
        metadata=_metadata(integration_data.get("metadata"), "integration.metadata"),
    )

    navigation: list[NavigationContract] = []
    for item in navigation_data:
        if not isinstance(item, Mapping):
            raise ValueError("Navigation entries must be mappings")
        navigation.append(
            NavigationContract(
                key=str(item.get("key", "")).strip(),
                label=str(item.get("label", "")).strip(),
                route=str(item.get("route", "")).strip(),
                module_code=str(item["module_code"]).strip() if item.get("module_code") is not None else None,
                icon=str(item["icon"]).strip() if item.get("icon") is not None else None,
                permission=str(item["permission"]).strip() if item.get("permission") is not None else None,
                entitlement=str(item["entitlement"]).strip() if item.get("entitlement") is not None else None,
                order=int(item.get("order", 0)),
                enabled=bool(item.get("enabled", True)),
                metadata=_metadata(item.get("metadata"), "navigation.metadata"),
            )
        )

    return ModuleRegistrationBundle(module=module, integration=integration, navigation=tuple(navigation))


def register_external_manifest(
    manifest: Mapping[str, object],
    module_registry: ModuleRegistry,
    navigation_registry: NavigationRegistry,
) -> None:
    """Register an external module from a plain-data manifest."""
    register_module(bundle_from_manifest(manifest), module_registry, navigation_registry)
