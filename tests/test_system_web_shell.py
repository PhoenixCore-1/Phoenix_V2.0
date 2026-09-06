from fastapi.testclient import TestClient

from phoenix_system.web.app import create_app


def test_system_registers_framework_modules() -> None:
    app = create_app()

    modules = app.state.module_registry.list()

    assert [module.code for module in modules] == [
        "crm",
        "sales",
        "inventory",
        "manufacturing",
        "procurement",
        "projects",
        "accounts",
    ]


def test_dashboard_renders_registered_modules() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert "CRM 360" in response.text
    assert "Inventory 360" in response.text
    assert "Manufacturing" in response.text
    assert "/modules/crm" in response.text


def test_module_route_uses_registry() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/inventory")

    assert response.status_code == 200
    assert "Inventory 360" in response.text
    assert "module code: <code>inventory</code>" in response.text


def test_unknown_module_is_not_a_valid_entry_point() -> None:
    client = TestClient(create_app())

    response = client.get("/modules/not-registered")

    assert response.status_code == 404


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "phoenix",
        "core": "v2",
    }
