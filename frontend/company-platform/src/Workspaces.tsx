import { useEffect, useState } from 'react'

type Workspace = {
  module_code: string
  module_name: string
  module_version: string
  display_name: string
  visible: boolean
  sort_order: number
  entitlement_status: string
}

export function Workspaces() {
  const [items, setItems] = useState<Workspace[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<string | null>(null)
  const [notice, setNotice] = useState('')

  const load = async () => {
    setLoading(true); setNotice('')
    try {
      const response = await fetch('/api/v1/company/workspaces', { credentials: 'include' })
      if (!response.ok) throw new Error('Unable to load workspaces')
      const body = await response.json() as { data?: { items?: Workspace[] } }
      setItems(body.data?.items ?? [])
    } catch {
      setNotice('Workspaces require an authenticated Phoenix Core session and the company workspace migration.')
    } finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [])

  const update = async (item: Workspace, patch: Partial<Workspace>) => {
    setSaving(item.module_code); setNotice('')
    try {
      const response = await fetch(`/api/v1/company/workspaces/${encodeURIComponent(item.module_code)}`, {
        method: 'PATCH', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patch),
      })
      const body = await response.json() as { data?: Workspace; message?: string }
      if (!response.ok || !body.data) throw new Error(body.message || 'Unable to save workspace')
      setItems((current) => current.map((entry) => entry.module_code === item.module_code ? body.data! : entry).sort((a, b) => a.sort_order - b.sort_order))
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to save workspace.')
    } finally { setSaving(null) }
  }

  return <div className="placeholder-panel" style={{ display: 'block' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 24, marginBottom: 24 }}>
      <div><span className="section-label">COMPANY WORKSPACES</span><h3 style={{ marginBottom: 6 }}>Workspace configuration</h3><p>Configure how entitled Phoenix workspaces are presented to company users. Module activation and licensing remain controlled by Phoenix System Platform.</p></div>
      <button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button>
    </div>
    {loading ? <p>Loading workspace configuration…</p> : items.length === 0 ? <p>{notice || 'No active module workspaces are available for this company.'}</p> : <div style={{ display: 'grid', gap: 12 }}>{items.map((item) => <div key={item.module_code} style={{ border: '1px solid rgba(15,32,56,.12)', borderRadius: 12, padding: 18, display: 'grid', gridTemplateColumns: '1fr auto', gap: 18, alignItems: 'center', background: '#fff' }}>
      <div><div style={{ fontSize: 11, fontWeight: 700, letterSpacing: '.08em', opacity: .55 }}>{item.module_code.toUpperCase()} · V{item.module_version}</div><strong style={{ display: 'block', fontSize: 17, margin: '5px 0' }}>{item.display_name}</strong><span style={{ fontSize: 13, opacity: .65 }}>Entitlement: {item.entitlement_status} · Order: {item.sort_order}</span></div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}><button className="refresh-button" disabled={saving === item.module_code} onClick={() => void update(item, { sort_order: Math.max(0, item.sort_order - 1) })}>↑</button><button className="refresh-button" disabled={saving === item.module_code} onClick={() => void update(item, { sort_order: item.sort_order + 1 })}>↓</button><button className={`access-pill ${item.visible ? 'active' : 'suspended'}`} style={{ border: 0, cursor: saving === item.module_code ? 'wait' : 'pointer' }} disabled={saving === item.module_code} onClick={() => void update(item, { visible: !item.visible })}>{item.visible ? 'VISIBLE' : 'HIDDEN'}</button></div>
    </div>)}</div>}
    {notice && !loading && <div className="inline-notice" style={{ marginTop: 16 }}>{notice}</div>}
  </div>
}
