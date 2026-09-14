import { useEffect, useState } from "react";

interface ReportData {
  organisation_id: string;
  people: { total_memberships: number; active: number; suspended: number; removed: number };
  roles: { total: number; active: number; disabled: number };
  security: { effective_permissions: number; available_permissions: number };
  modules: { entitled: string[] };
  report_scope: string;
}

export default function Reports() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/v1/company/reports", { credentials: "include" })
      .then(async (response) => {
        const body = await response.json();
        if (!response.ok) throw new Error(body?.detail?.message || body?.detail || "Unable to load company report.");
        return body.data as ReportData;
      })
      .then(setReport)
      .catch((err) => setError(err instanceof Error ? err.message : "Unable to load company report."));
  }, []);

  if (error) return <section className="workspace"><div className="panel"><h2>Company Reports</h2><p className="error">{error}</p></div></section>;
  if (!report) return <section className="workspace"><div className="panel"><h2>Company Reports</h2><p>Loading company administration report…</p></div></section>;

  return (
    <section className="workspace">
      <div className="workspace-heading">
        <div>
          <p className="eyebrow">COMPANY PLATFORM</p>
          <h1>Company Reports</h1>
          <p>Tenant-level administration and oversight.</p>
        </div>
        <span className="authority-badge">PHOENIX CORE</span>
      </div>

      <div className="report-grid">
        <div className="panel"><p className="eyebrow">PEOPLE</p><strong className="metric">{report.people.total_memberships}</strong><p>Total memberships</p><div className="metric-row"><span>Active {report.people.active}</span><span>Suspended {report.people.suspended}</span><span>Removed {report.people.removed}</span></div></div>
        <div className="panel"><p className="eyebrow">ROLES</p><strong className="metric">{report.roles.total}</strong><p>Total roles</p><div className="metric-row"><span>Active {report.roles.active}</span><span>Disabled {report.roles.disabled}</span></div></div>
        <div className="panel"><p className="eyebrow">SECURITY</p><strong className="metric">{report.security.effective_permissions}</strong><p>Effective permissions</p><div className="metric-row"><span>Available {report.security.available_permissions}</span></div></div>
        <div className="panel"><p className="eyebrow">MODULES</p><strong className="metric">{report.modules.entitled.length}</strong><p>Entitled modules</p><div className="tag-list">{report.modules.entitled.length ? report.modules.entitled.map((module) => <span className="tag" key={module}>{module}</span>) : <span>No entitled modules</span>}</div></div>
      </div>

      <div className="panel report-note">
        <p className="eyebrow">REPORT SCOPE</p>
        <h3>Company Administration</h3>
        <p>This report provides Company Platform administration and oversight information. Operational business reporting belongs to the relevant Phoenix business modules.</p>
      </div>
    </section>
  );
}
