import { useEffect, useState } from 'react'

type Evidence = {
  id: string
  evidence_type: string
  title: string
  description?: string | null
  status: string
  valid_from?: string | null
  valid_until?: string | null
  policy_version_id?: string | null
  document_id?: string | null
  document_version_id?: string | null
}

export function Evidence() {
  const [items, setItems] = useState<Evidence[]>([])
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')
  const load = async () => {
    setLoading(true); setNotice('')
    try {
      const response = await fetch('/api/v1/company/evidence', { credentials: 'include' })
      const body = await response.json() as { data?: { items?: Evidence[] }; message?: string }
      if (!response.ok) throw new Error(body.message || 'Unable to load company evidence.')
      setItems(body.data?.items ?? [])
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load company evidence.') }
    finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])
  return <div className="people-page">
    <div className="people-toolbar">
      <div><span className="section-label">COMPLIANCE & LEGAL</span><h3 style={{ margin: '5px 0' }}>Evidence</h3><p style={{ margin: 0, color: '#627287', fontSize: 11 }}>Tenant evidence records linked to authoritative Core documents and legal versions.</p></div>
      <button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button>
    </div>
    <div className="access-summary">
      <div><span>ACTIVE</span><strong>{items.filter(i => i.status === 'ACTIVE').length}</strong></div>
      <div><span>EXPIRED</span><strong>{items.filter(i => i.status === 'EXPIRED').length}</strong></div>
      <div><span>ARCHIVED</span><strong>{items.filter(i => i.status === 'ARCHIVED').length}</strong></div>
      <div><span>AUTHORITY</span><strong>Core</strong></div>
    </div>
    <div className="people-table-wrap"><table className="people-table"><thead><tr><th>EVIDENCE</th><th>TYPE</th><th>VALID UNTIL</th><th>DOCUMENT</th><th>STATUS</th></tr></thead><tbody>
      {loading ? <tr><td colSpan={5} className="table-empty">Loading evidence…</td></tr> : items.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No company evidence records have been added.'}</td></tr> : items.map(item => <tr key={item.id}><td><strong>{item.title}</strong><div style={{ marginTop: 3, color: '#8290a0', fontSize: 9 }}>{item.description || 'No description'}</div></td><td>{item.evidence_type}</td><td>{item.valid_until ? new Date(item.valid_until).toLocaleDateString() : '—'}</td><td>{item.document_version_id || item.document_id ? 'Linked' : 'Not linked'}</td><td><span className={`access-pill ${item.status.toLowerCase()}`}>{item.status}</span></td></tr>)}
    </tbody></table></div>
    {notice && <div className="inline-notice">{notice}</div>}
    <div className="boundary-note"><strong>Evidence authority</strong><p>Company Platform owns the tenant evidence record and its compliance context. Phoenix Core remains authoritative for identity, tenant scope, documents, document versions, legal records and audit history.</p></div>
  </div>
}
