from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CORE_ROOT = PROJECT_ROOT / "src" / "phoenix_core"
FRAMEWORK_ROOT = PROJECT_ROOT / "src" / "phoenix_framework"


def all_python_files(root: Path):
    return root.rglob("*.py")


def read_python(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def test_core_has_no_framework_dependency():
    for path in all_python_files(CORE_ROOT):
        text = read_python(path)

        assert "phoenix_framework" not in text, (
            f"Core must not depend on Generic Framework: {path}"
        )


def test_framework_has_no_direct_sql_dependency():
    forbidden = (
        "import sqlite3",
        "from sqlite3",
        "cursor.execute(",
        "connection.execute(",
        "conn.execute(",
    )

    for path in all_python_files(FRAMEWORK_ROOT):
        text = read_python(path)

        for marker in forbidden:
            assert marker not in text, (
                f"Framework contains direct database access '{marker}': {path}"
            )


def test_framework_has_no_database_infrastructure_dependency():
    forbidden = (
        "phoenix_core.infrastructure",
        "sqlitedatabase",
        "phoenix_core.migrations",
    )

    for path in all_python_files(FRAMEWORK_ROOT):
        text = read_python(path)

        for marker in forbidden:
            assert marker not in text, (
                f"Framework contains database infrastructure dependency "
                f"'{marker}': {path}"
            )


def test_framework_has_no_business_module_dependency():
    forbidden = (
        "phoenix_crm",
        "phoenix_sales",
        "phoenix_production",
        "phoenix_inventory",
        "phoenix_procurement",
        "phoenix_accounts",
        "phoenix_projects",
    )

    for path in all_python_files(FRAMEWORK_ROOT):
        text = read_python(path)

        for marker in forbidden:
            assert marker not in text, (
                f"Framework contains business-module dependency "
                f"'{marker}': {path}"
            )


def test_framework_has_no_provider_specific_ai_dependency():
    forbidden = (
        "openai",
        "anthropic",
        "google.generativeai",
        "azure.ai",
    )

    for path in all_python_files(FRAMEWORK_ROOT):
        text = read_python(path)

        for marker in forbidden:
            assert marker not in text, (
                f"Framework contains provider-specific AI dependency "
                f"'{marker}': {path}"
            )


def test_framework_does_not_define_core_authority_classes():
    forbidden_class_names = (
        "identityservice",
        "authenticationservice",
        "organisationservice",
        "membershipservice",
        "permissionservice",
        "roleservice",
        "entitlementservice",
        "auditservice",
        "sessionservice",
    )

    for path in all_python_files(FRAMEWORK_ROOT):
        text = read_python(path)

        for class_name in forbidden_class_names:
            assert f"class {class_name}" not in text, (
                f"Framework appears to define duplicate Core authority "
                f"'{class_name}': {path}"
            )


def test_framework_package_has_expected_boundaries():
    expected = (
        FRAMEWORK_ROOT / "contracts",
        FRAMEWORK_ROOT / "context",
        FRAMEWORK_ROOT / "modules",
        FRAMEWORK_ROOT / "navigation",
        FRAMEWORK_ROOT / "platform",
    )

    for directory in expected:
        assert directory.is_dir(), f"Missing Framework boundary: {directory}"
        assert (directory / "__init__.py").is_file(), (
            f"Missing package initializer: {directory}"
        )


def test_framework_has_single_package_authority():
    assert (FRAMEWORK_ROOT / "__init__.py").is_file()
    assert FRAMEWORK_ROOT.name == "phoenix_framework"
