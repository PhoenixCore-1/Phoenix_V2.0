import { useEffect, useState } from 'react'

type ComplianceItem = {
  policy_id: string
  policy_code: string
  policy_type: string
  required_acceptance: boolean
  version: { number: number; label: string; document_id: string; effective_at: string; status: string }
  acceptance_required: boolean
  acceptance_count: number
  current_identity_accepted: boolean
  status: string
}

type ComplianceResponse = {
  summary: { active_requirements: number; current_identity_accepted: number; action_required: number; status: string }
  items: ComplianceItem[]
  capabilities: { requirements: boolean; policy_versions: boolean; acceptance_status: boolean; contracts: boolean; evidence_records: boolean }
}

export function Compliance() {
  const [data, setData] = useState<ComplianceResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')

  const load = async () => {
    setLoading(true); setNotice('')
    try {
      const response = await fetch('/api/v1/company/compliance', { credentials: 'include' })
      const body = await response.json() as { data?: ComplianceResponse; message?: string }
      if (!response.ok) throw new Error(body.message || 'Unable to load company compliance.')
      setData(body.data ?? null)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to load company compliance.')
    } finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [])

  return <div className="people-page">
    <div className="people-toolbar">
      <div><span className="section-label">COMPLIANCE & LEGAL</span><h3 style={{ margin: '5px 0' }}>Company compliance</h3><p style={{ margin: 0, color: '#627287', fontSize: 11 }}>Company-level oversight of published Core legal requirements and acceptance status.</p></div>
      <button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button>
    </div>
    <div className="access-summary">
      <div><span>REQUIRED</span><strong>{data?.summary.active_requirements ?? '—'}</strong></div>
      <div><span>ACCEPTED</span><strong>{data?.summary.current_identity_accepted ?? '—'}</strong></div>
      <div><span>ACTION REQUIRED</span><strong>{data?.summary.action_required ?? '—'}</strong></div>
      <div><span>AUTHORITY</span><strong>Core Legal</strong></div>
    </div>
    <div className="people-table-wrap">
      <table className="people-table">
        <thead><tr><th>REQUIREMENT</th><th>VERSION</th><th>EFFECTIVE</th><th>ACCEPTANCES</th><th>STATUS</th></tr></thead>
        <tbody>
          {loading ? <tr><td colSpan={5} className="table-empty">Loading compliance records…</td></tr> : !data || data.items.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No active company legal requirements are currently published.'}</td></tr> : data.items.map((item) => <tr key={`${item.policy_id}-${item.version.number}`}>
            <td><strong>{item.policy_code}</strong><div style={{ marginTop: 3, color: '#8290a0', fontSize: 9 }}>{item.policy_type}</div></td>
            <td>{item.version.label || `v${item.version.number}`}</td>
            <td>{new Date(item.version.effective_at).toLocaleDateString()}</td>
            <td>{item.acceptance_count}</td>
            <td><span className={`access-pill ${item.current_identity_accepted ? 'active' : item.acceptance_required ? 'suspended' : 'active'}`}>{item.status.replace(/_/g, ' ')}</span></td>
          </tr>)}
        </tbody>
      </table>
    </div>
    {notice && <div className="inline-notice">{notice}</div>}
    <div className="boundary-note"><strong>Legal boundary</strong><p>System Platform owns the Phoenix-wide Regulatory & Legal framework. Company Platform provides tenant Compliance & Legal oversight. Legal records, document versions, acceptance evidence and audit remain authoritative in Phoenix Core.</p></div>
    {data && <div className="boundary-note"><strong>Current capability</strong><p>Requirements, published versions and acceptance status are connected. Company contracts and dedicated evidence-record management are intentionally not enabled until their authoritative Core models are implemented.</p></div>}
  </div>
}
