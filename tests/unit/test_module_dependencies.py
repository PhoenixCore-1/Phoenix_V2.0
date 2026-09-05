import pytest

from phoenix_framework.contracts import ModuleDependency, ModuleIntegrationContract
from phoenix_framework.dependencies import validate_dependencies


def contract(code, version, dependencies=(), capabilities=()):
    return ModuleIntegrationContract(
        module_code=code,
        version=version,
        provided_capabilities=capabilities,
        dependencies=dependencies,
    )


def test_required_dependency_and_capability_are_validated():
    sales = contract(
        "sales", "1.0.0",
        dependencies=(ModuleDependency("crm", minimum_version="1.2.0", capabilities=("crm.customers",)),),
    )
    crm = contract("crm", "1.3.0", capabilities=("crm.customers",))
    assert validate_dependencies((sales, crm)) == ()


def test_missing_required_dependency_is_reported():
    sales = contract("sales", "1.0.0", dependencies=(ModuleDependency("crm"),))
    issues = validate_dependencies((sales,))
    assert issues[0].reason == "missing required module"


def test_incompatible_version_and_missing_capability_are_reported():
    sales = contract(
        "sales", "1.0.0",
        dependencies=(ModuleDependency("crm", minimum_version="2.0.0", capabilities=("crm.customers",)),),
    )
    crm = contract("crm", "1.5.0")
    reasons = {issue.reason for issue in validate_dependencies((sales, crm))}
    assert "incompatible version" in reasons
    assert "missing capability: crm.customers" in reasons


def test_optional_missing_dependency_does_not_fail_validation():
    sales = contract("sales", "1.0.0", dependencies=(ModuleDependency("crm", required=False),))
    assert validate_dependencies((sales,)) == ()


def test_circular_dependency_is_reported():
    sales = contract("sales", "1.0.0", dependencies=(ModuleDependency("crm"),))
    crm = contract("crm", "1.0.0", dependencies=(ModuleDependency("sales"),))
    issues = validate_dependencies((sales, crm))
    assert any(issue.reason == "circular dependency" for issue in issues)


def test_duplicate_contracts_are_rejected():
    with pytest.raises(ValueError, match="Duplicate integration contract"):
        validate_dependencies((contract("sales", "1.0.0"), contract("sales", "1.1.0")))
