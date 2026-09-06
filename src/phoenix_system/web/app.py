"""Phoenix System web entry point.

This is intentionally a thin presentation layer over Phoenix Core V2.
Core remains responsible for identity, tenancy, authorization and module
registration; the landing page only renders the application shell.
"""

from html import escape

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Phoenix", version="0.1.0")

MODULES = [
    ("crm", "CRM 360"),
    ("sales", "Sales 360"),
    ("inventory", "Inventory 360"),
    ("manufacturing", "Manufacturing"),
    ("procurement", "Procurement"),
    ("projects", "Projects"),
    ("accounts", "Accounts"),
]


def landing_page() -> str:
    nav = "".join(
        f'<a href="/modules/{escape(code)}">{escape(name)}</a>'
        for code, name in MODULES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Phoenix</title>
<style>
:root {{ --navy:#0d1b2a; --blue:#1677ff; --gold:#d6a84f; --bg:#f5f7fa; --text:#17212b; --muted:#697586; --border:#e4e8ee; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,Segoe UI,Arial,sans-serif; color:var(--text); background:var(--bg); }}
.shell {{ min-height:100vh; display:grid; grid-template-columns:240px 1fr; grid-template-rows:64px 1fr; }}
header {{ grid-column:1/-1; background:var(--navy); color:white; display:flex; align-items:center; padding:0 24px; border-bottom:3px solid var(--gold); }}
.brand {{ font-weight:700; letter-spacing:.04em; font-size:20px; }}
.context {{ margin-left:auto; font-size:13px; opacity:.8; }}
aside {{ background:#111f2e; padding:22px 14px; }}
aside .label {{ color:#8d9aaa; font-size:11px; text-transform:uppercase; letter-spacing:.1em; padding:0 12px 10px; }}
aside a {{ display:block; color:#dce4ed; text-decoration:none; padding:11px 12px; border-radius:7px; font-size:14px; margin-bottom:3px; }}
aside a:hover {{ background:#1d3044; color:white; }}
main {{ padding:34px; max-width:1400px; width:100%; }}
.eyebrow {{ color:var(--blue); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; }}
h1 {{ margin:7px 0 8px; font-size:30px; }}
.subtitle {{ color:var(--muted); margin:0 0 28px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; }}
.card {{ background:white; border:1px solid var(--border); border-radius:10px; padding:22px; min-height:130px; box-shadow:0 2px 7px rgba(20,30,40,.04); }}
.card h2 {{ font-size:17px; margin:0 0 8px; }}
.card p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.5; }}
.status {{ margin-top:28px; background:white; border:1px solid var(--border); border-radius:10px; padding:20px; }}
.status strong {{ color:#218739; }}
@media(max-width:760px) {{ .shell {{ grid-template-columns:1fr; grid-template-rows:64px auto 1fr; }} aside {{ grid-column:1; }} main {{ padding:22px; }} }}
</style>
</head>
<body>
<div class="shell">
<header><div class="brand">PHOENIX</div><div class="context">Core V2.0 · System</div></header>
<aside><div class="label">Workspace</div><a href="/">Dashboard</a>{nav}<div class="label" style="margin-top:22px">Administration</div><a href="/">System</a></aside>
<main>
<div class="eyebrow">Phoenix Core</div>
<h1>Welcome to Phoenix</h1>
<p class="subtitle">The Phoenix application shell is connected to the Core foundation. Business modules register into this workspace independently.</p>
<div class="grid">{''.join(f'<section class="card"><h2>{escape(name)}</h2><p>Module entry point reserved for the registered {escape(name)} capability.</p></section>' for _, name in MODULES)}</div>
<div class="status">Core foundation: <strong>connected</strong> · Tenant and authorization services remain authoritative in Phoenix Core.</div>
</main>
</div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def landing() -> str:
    return landing_page()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "application": "phoenix", "core": "v2"}
