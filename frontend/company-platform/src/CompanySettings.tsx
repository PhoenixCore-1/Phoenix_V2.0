import { useEffect, useState } from 'react'

type Setting = {
  id: string
  organisation_id: string
  key: string
  value_type: string
  value: unknown
  description?: string | null
  updated_at: string
}

export function CompanySettings() {
  const [items, setItems] = useState<Setting[]>([])
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')

  const load = async () => {
    setLoading(true)
    setNotice('')
    try {
      const response = await fetch('/api/v1/company/settings', { credentials: 'include' })
      if (!response.ok) throw new Error('Unable to load company settings')
      const body = await response.json() as { data?: { items?: Setting[] } }
      setItems(body.data?.items ?? [])
    } catch {
      setNotice('Company settings require an authenticated Phoenix Core session with company configuration permission.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  return <div className="people-page">
    <div className="people-toolbar">
      <div><span className="section-label">COMPANY SETTINGS</span><h3 style={{ margin: '5px 0' }}>Company configuration</h3></div>
      <button className="refresh-button" onClick={() => void load()}>Refresh</button>
    </div>
    <div className="access-summary">
      <div><span>COMPANY SCOPE</span><strong>Tenant</strong></div>
      <div><span>AUTHORITY</span><strong>Core</strong></div>
      <div><span>SETTINGS</span><strong>{items.length}</strong></div>
      <div><span>GLOBAL CONTROL</span><strong>System Platform</strong></div>
    </div>
    <div className="people-table-wrap">
      <table className="people-table">
        <thead><tr><th>SETTING</th><th>TYPE</th><th>VALUE</th><th>DESCRIPTION</th><th>UPDATED</th></tr></thead>
        <tbody>
          {loading ? <tr><td colSpan={5} className="table-empty">Loading company settings…</td></tr> : items.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No tenant settings configured.'}</td></tr> : items.map((item) => <tr key={item.id}>
            <td><strong>{item.key}</strong></td><td>{item.value_type}</td><td>{typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value)}</td><td>{item.description || '—'}</td><td>{new Date(item.updated_at).toLocaleString()}</td>
          </tr>)}
        </tbody>
      </table>
    </div>
    {notice && <div className="inline-notice">{notice}</div>}
    <div className="boundary-note"><strong>Company Platform boundary</strong><p>These settings are tenant-scoped configuration only. Phoenix System Platform remains responsible for global platform settings, licensing, subscriptions and module activation.</p></div>
  </div>
}
