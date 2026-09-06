from fastapi.testclient import TestClient

from phoenix_system.services.authentication import AuthenticationService
from phoenix_system.web.app import create_app


def make_client() -> TestClient:
    auth = AuthenticationService(username="admin", password="correct")
    return TestClient(
        create_app(auth_service=auth),
        base_url="https://testserver",
    )


def test_login_page_is_public() -> None:
    client = make_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert "Sign in" in response.text
    assert 'name="username"' in response.text
    assert 'name="password"' in response.text


def test_unauthenticated_dashboard_redirects_to_login() -> None:
    client = make_client()

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_unauthenticated_module_route_redirects_to_login() -> None:
    client = make_client()

    response = client.get("/modules/inventory", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_invalid_login_is_rejected() -> None:
    client = make_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    assert "Invalid username or password." in response.text


def test_valid_login_creates_authenticated_session() -> None:
    client = make_client()

    response = client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert "phoenix_session=" in response.headers["set-cookie"]
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "Secure" in response.headers["set-cookie"]

    dashboard = client.get("/")

    assert dashboard.status_code == 200
    assert "Welcome to Phoenix" in dashboard.text
    assert "Welcome, Phoenix Administrator." in dashboard.text


def test_authenticated_user_can_access_modules() -> None:
    client = make_client()

    login = client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
    )

    assert login.status_code == 200

    response = client.get("/modules/inventory")

    assert response.status_code == 200
    assert "Inventory 360" in response.text


def test_logout_revokes_session() -> None:
    client = make_client()

    login = client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
    )

    assert login.status_code == 200
    assert client.get("/").status_code == 200

    logout = client.post("/logout", follow_redirects=False)

    assert logout.status_code == 303
    assert logout.headers["location"] == "/login"

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_system_registers_framework_modules() -> None:
    app = create_app(
        auth_service=AuthenticationService(
            username="admin",
            password="correct",
        )
    )

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
    client = make_client()

    client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
    )

    response = client.get("/")

    assert response.status_code == 200
    assert "CRM 360" in response.text
    assert "Inventory 360" in response.text
    assert "Manufacturing" in response.text
    assert "/modules/crm" in response.text


def test_unknown_module_is_not_a_valid_entry_point() -> None:
    client = make_client()

    client.post(
        "/login",
        data={"username": "admin", "password": "correct"},
    )

    response = client.get("/modules/not-registered")

    assert response.status_code == 404


def test_health_endpoint_remains_public() -> None:
    client = make_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "phoenix",
        "core": "v2",
    }
