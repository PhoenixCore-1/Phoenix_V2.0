"""Phoenix System web application shell.

The web layer is a presentation adapter. Phoenix Core remains authoritative
for identity, tenancy, authorization, entitlements and access scope.
"""

from html import escape

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from phoenix_framework.navigation.registry import NavigationRegistry
from phoenix_framework.modules.registry import ModuleRegistry

from .modules import enabled_modules, register_system_modules
from .navigation import register_default_navigation, visible_navigation
from .pages import PageRegistry, register_system_pages


PHOENIX_LOGO_URL = "/phoenix_logo.png"


def create_app() -> FastAPI:
    """Create the Phoenix System presentation application."""
    application = FastAPI(title="Phoenix", version="0.1.0")

    module_registry = ModuleRegistry()
    navigation_registry = NavigationRegistry()
    page_registry = PageRegistry()

    register_system_modules(module_registry)
    register_default_navigation(navigation_registry)
    register_system_pages(page_registry)

    application.state.module_registry = module_registry
    application.state.navigation_registry = navigation_registry
    application.state.page_registry = page_registry

    @application.get("/", response_class=HTMLResponse)
    def landing() -> str:
        return render_dashboard(application)

    @application.get("/system", response_class=HTMLResponse)
    def system_page() -> str:
        return render_system_page(application)

    @application.get("/modules/{module_code}", response_class=HTMLResponse)
    def module_entry(module_code: str) -> str:
        try:
            module = application.state.module_registry.get(module_code)
        except ValueError:
            raise HTTPException(status_code=404, detail="Module not registered") from None
        if not module.enabled:
            raise HTTPException(status_code=404, detail="Module not enabled")
        return render_module_entry(module.code, module.name, module.description)

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "application": "phoenix", "core": "v2"}

    return application


def render_dashboard(application: FastAPI) -> str:
    modules = enabled_modules(application.state.module_registry)
    nav = visible_navigation(application.state.navigation_registry)
    return _page(
        title="Dashboard",
        active="Dashboard",
        nav_items=nav,
        body=f"""
        <div class="eyebrow">Phoenix System</div>
        <h1>Welcome to Phoenix</h1>
        <p class="subtitle">Your connected business platform, presented through one System shell and the Phoenix Generic Framework.</p>
        <div class="grid">{''.join(_module_card(module.code, module.name, module.description) for module in modules)}</div>
        <section class="status"><div><span class="dot"></span><strong>Core foundation connected</strong></div><p>Identity, tenancy, authorization, entitlements and access scope remain authoritative in Phoenix Core.</p></section>
        """,
    )


def render_system_page(application: FastAPI) -> str:
    modules = enabled_modules(application.state.module_registry)
    return _page(
        title="System",
        active="System",
        nav_items=visible_navigation(application.state.navigation_registry),
        body=f"""
        <div class="eyebrow">Administration</div>
        <h1>System Platform</h1>
        <p class="subtitle">Configure the company workspace and manage the platform foundation without embedding business logic in the System shell.</p>
        <div class="admin-grid">
          <article><span>01</span><h2>Company</h2><p>Company identity, branding, locations and organisation structure.</p></article>
          <article><span>02</span><h2>Users &amp; Roles</h2><p>Platform access, roles, permissions and user configuration.</p></article>
          <article><span>03</span><h2>Modules</h2><p>{len(modules)} framework module descriptors are currently registered for presentation.</p></article>
          <article><span>04</span><h2>Pages &amp; Workspaces</h2><p>Configure layouts and eventually use the Phoenix Page Designer.</p></article>
        </div>
        """,
    )


def render_module_entry(code: str, name: str, description: str) -> str:
    return _page(
        title=name,
        active=name,
        nav_items=(),
        body=f"""
        <div class="eyebrow">Registered module</div>
        <h1>{escape(name)}</h1>
        <p class="subtitle">{escape(description)}</p>
        <section class="status"><div><span class="dot"></span><strong>Framework entry point</strong></div><p>Module code: <code>{escape(code)}</code>. The business module will contribute its own pages, navigation and components.</p></section>
        """,
    )


def _module_card(code: str, name: str, description: str) -> str:
    return f'<a class="card" href="/modules/{escape(code)}"><span class="card-kicker">MODULE</span><h2>{escape(name)}</h2><p>{escape(description)}</p><span class="arrow">→</span></a>'


def _page(*, title: str, active: str, nav_items: list, body: str) -> str:
    nav = ''.join(
        f'<a class="{"active" if item.label == active else ""}" href="{escape(item.route)}">{escape(item.label)}</a>'
        for item in nav_items
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · Phoenix</title>
<style>
:root{{--navy:#061a33;--navy2:#071b35;--blue:#123d6b;--gold:#d3a63a;--bg:#f4f7fb;--text:#15263b;--muted:#68788c;--border:#dbe3ed;--white:#fff}}
*{{box-sizing:border-box}}body{{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--text)}}
.shell{{min-height:100vh;display:grid;grid-template-columns:258px 1fr;grid-template-rows:76px 1fr}}header{{grid-column:1/-1;background:var(--navy);color:white;display:flex;align-items:center;padding:0 26px;border-bottom:3px solid var(--gold)}}
.brand{{display:flex;align-items:center;gap:12px;text-decoration:none;color:#fff;min-width:190px}}.brand img{{width:44px;height:44px;object-fit:contain;border-radius:7px;background:#fff;padding:3px}}.brand-copy{{display:flex;flex-direction:column}}.brand-name{{font-size:21px;font-weight:800;line-height:1}}.brand-sub{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#c3cfdd;margin-top:5px;font-weight:600}}.brand-fallback{{display:none;font-size:21px;font-weight:800;letter-spacing:.08em}}.context{{margin-left:auto;color:#c8d3df;font-size:13px}}
aside{{background:var(--navy2);padding:24px 14px}}.label{{padding:0 12px 9px;color:#8190a0;font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}}aside a{{display:block;padding:11px 12px;margin:3px 0;border-radius:7px;color:#dbe4ed;text-decoration:none;font-size:14px}}aside a:hover,aside a.active{{background:#173a5f;color:white}}main{{padding:38px;max-width:1450px;width:100%}}.eyebrow{{color:var(--gold);font-size:11px;font-weight:800;letter-spacing:.12em;text-transform:uppercase}}h1{{margin:7px 0 8px;font-size:31px}}.subtitle{{max-width:820px;color:var(--muted);line-height:1.55;margin:0 0 30px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px}}.card{{position:relative;display:block;min-height:150px;background:var(--white);border:1px solid var(--border);border-radius:11px;padding:22px;text-decoration:none;color:var(--text);transition:.15s ease}}.card:hover{{transform:translateY(-2px);border-color:#bfcbd8;box-shadow:0 7px 22px rgba(16,35,55,.07)}}.card-kicker{{font-size:10px;color:var(--blue);font-weight:800;letter-spacing:.1em}}.card h2{{margin:9px 0 7px;font-size:18px}}.card p,article p{{margin:0;color:var(--muted);font-size:13px;line-height:1.5}}.arrow{{position:absolute;right:20px;bottom:18px;color:var(--gold);font-size:20px}}.status{{margin-top:22px;background:var(--white);border:1px solid var(--border);border-top:3px solid var(--gold);border-radius:11px;padding:20px 22px}}.status div{{display:flex;align-items:center;gap:9px}}.status strong{{font-size:14px}}.status p{{margin:8px 0 0;color:var(--muted);font-size:13px}}.dot{{width:8px;height:8px;border-radius:50%;background:#2da45a;display:inline-block}}.admin-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}article{{background:white;border:1px solid var(--border);border-radius:11px;padding:23px}}article span{{font-size:11px;color:var(--blue);font-weight:800}}article h2{{margin:8px 0 7px;font-size:18px}}code{{font-family:Consolas,monospace;color:var(--blue)}}
@media(max-width:760px){{.shell{{grid-template-columns:1fr;grid-template-rows:76px auto 1fr}}aside{{padding:14px}}main{{padding:24px}}.admin-grid{{grid-template-columns:1fr}}.context{{display:none}}}}
</style></head><body><div class="shell"><header><a class="brand" href="/" aria-label="Phoenix home"><img src="{PHOENIX_LOGO_URL}" alt="Phoenix" onerror="this.style.display='none';this.nextElementSibling.querySelector('.brand-fallback').style.display='block'"><span class="brand-copy"><span class="brand-name">Phoenix</span><span class="brand-sub">Core Platform</span><span class="brand-fallback">PHOENIX</span></span></a><div class="context">Core V2.0 · Company Workspace</div></header><aside><div class="label">Workspace</div>{nav}<div class="label" style="margin-top:24px">Administration</div><a class="{"active" if active == "System" else ""}" href="/system">System</a></aside><main>{body}</main></div></body></html>"""


app = create_app()
