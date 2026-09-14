import { useEffect, useMemo, useState } from 'react'

type ActivityItem = { id: string; identity_id: string | null; action: string; target_type: string | null; target_id: string | null; request_id: string | null; created_at: string }

function label(value: string) {
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())
}

export function Activity() {
  const [items, setItems] = useState<ActivityItem[]>([])
  const [query, setQuery] = useState('')
  const [target, setTarget] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')

  const load = async () => {
    setLoading(true); setNotice('')
    try {
      const response = await fetch('/api/v1/company/activity?limit=100', { credentials: 'include' })
      const body = await response.json() as { data?: { items?: ActivityItem[] }; message?: string }
      if (!response.ok) throw new Error(body.message || 'Unable to load company activity.')
      setItems(body.data?.items ?? [])
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load company activity.') }
    finally { setLoading(false) }
  }
  useEffect(() => { void load() }, [])

  const targets = useMemo(() => ['ALL', ...Array.from(new Set(items.map((item) => item.target_type).filter(Boolean) as string[]))], [items])
  const filtered = useMemo(() => items.filter((item) => {
    const text = `${item.action} ${item.target_type ?? ''} ${item.identity_id ?? ''} ${item.request_id ?? ''}`.toLowerCase()
    return text.includes(query.toLowerCase()) && (target === 'ALL' || item.target_type === target)
  }), [items, query, target])

  return <div className="people-page">
    <div className="people-toolbar"><div><span className="section-label">COMPANY ACTIVITY</span><h3 style={{ margin: '5px 0' }}>Activity & oversight</h3><p style={{ margin: 0, color: '#627287', fontSize: 11 }}>Read-only company activity sourced from Phoenix Core audit events.</p></div><button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
    <div className="access-summary"><div><span>EVENTS LOADED</span><strong>{items.length}</strong></div><div><span>VISIBLE</span><strong>{filtered.length}</strong></div><div><span>AUTHORITY</span><strong>Core Audit</strong></div><div><span>MODE</span><strong>Read-only</strong></div></div>
    <div className="people-controls"><label className="search-field"><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search activity..." /></label><select value={target} onChange={(e) => setTarget(e.target.value)}>{targets.map((item) => <option key={item} value={item}>{item === 'ALL' ? 'All targets' : label(item)}</option>)}</select></div>
    <div className="people-table-wrap"><table className="people-table"><thead><tr><th>TIME</th><th>ACTIVITY</th><th>TARGET</th><th>IDENTITY</th><th>REQUEST</th></tr></thead><tbody>{loading ? <tr><td colSpan={5} className="table-empty">Loading company activity…</td></tr> : filtered.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No company activity returned from Phoenix Core.'}</td></tr> : filtered.map((item) => <tr key={item.id}><td>{new Date(item.created_at).toLocaleString()}</td><td><strong>{label(item.action)}</strong></td><td>{item.target_type ? `${label(item.target_type)}${item.target_id ? ` · ${item.target_id.slice(0, 8)}` : ''}` : '—'}</td><td>{item.identity_id ? item.identity_id.slice(0, 8) : 'System'}</td><td>{item.request_id ? item.request_id.slice(0, 8) : '—'}</td></tr>)}</tbody></table></div>
    {notice && <div className="inline-notice">{notice}</div>}
  </div>
}
