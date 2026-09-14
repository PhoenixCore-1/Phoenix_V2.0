import { FormEvent, useEffect, useState } from 'react'

type Setting = {
  id: string
  organisation_id: string
  key: string
  value_type: string
  value: unknown
  description?: string | null
  updated_at: string
}

type SettingPayload = { value: unknown; value_type?: string; description?: string }

function displayValue(value: unknown) {
  return typeof value === 'object' ? JSON.stringify(value) : String(value)
}

function valueForEditor(value: unknown, valueType: string) {
  if (valueType === 'json') return JSON.stringify(value, null, 2)
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  return String(value ?? '')
}

function parseValue(raw: string, valueType: string): unknown {
  if (valueType === 'boolean') {
    if (raw.trim().toLowerCase() === 'true') return true
    if (raw.trim().toLowerCase() === 'false') return false
    throw new Error('Boolean settings must be true or false.')
  }
  if (valueType === 'integer') {
    const value = Number.parseInt(raw, 10)
    if (!Number.isInteger(value)) throw new Error('Integer settings must contain a whole number.')
    return value
  }
  if (valueType === 'number') {
    const value = Number(raw)
    if (!Number.isFinite(value)) throw new Error('Number settings must contain a valid number.')
    return value
  }
  if (valueType === 'json') {
    try { return JSON.parse(raw) } catch { throw new Error('JSON settings must contain valid JSON.') }
  }
  return raw
}

export function CompanySettings() {
  const [items, setItems] = useState<Setting[]>([])
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState('')
  const [editing, setEditing] = useState<Setting | null>(null)
  const [value, setValue] = useState('')
  const [description, setDescription] = useState('')
  const [saving, setSaving] = useState(false)

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

  const beginEdit = (item: Setting) => {
    setEditing(item)
    setValue(valueForEditor(item.value, item.value_type))
    setDescription(item.description ?? '')
    setNotice('')
  }

  const cancelEdit = () => {
    setEditing(null)
    setValue('')
    setDescription('')
  }

  const save = async (event: FormEvent) => {
    event.preventDefault()
    if (!editing) return
    setSaving(true)
    setNotice('')
    try {
      const payload: SettingPayload = { value: parseValue(value, editing.value_type) }
      if (description.trim()) payload.description = description.trim()
      const response = await fetch(`/api/v1/company/settings/${encodeURIComponent(editing.key)}`, {
        method: 'PATCH',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const body = await response.json().catch(() => ({})) as { error?: {message?: string}; data?: { item?: Setting } }
      if (!response.ok) throw new Error(body.error?.message || 'Unable to save company setting.')
      if (body.data?.item) setItems((current) => current.map((item) => item.key === editing.key ? body.data!.item! : item))
      else await load()
      cancelEdit()
      setNotice(`Saved ${editing.key}.`)
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to save company setting.')
    } finally {
      setSaving(false)
    }
  }

  return <div className="people-page">
    <div className="people-toolbar">
      <div><span className="section-label">COMPANY SETTINGS</span><h3 style={{ margin: '5px 0' }}>Company configuration</h3></div>
      <button className="refresh-button" onClick={() => void load()} disabled={loading || saving}>Refresh</button>
    </div>
    <div className="access-summary">
      <div><span>COMPANY SCOPE</span><strong>Tenant</strong></div>
      <div><span>AUTHORITY</span><strong>Core</strong></div>
      <div><span>SETTINGS</span><strong>{items.length}</strong></div>
      <div><span>GLOBAL CONTROL</span><strong>System Platform</strong></div>
    </div>
    <div className="people-table-wrap">
      <table className="people-table">
        <thead><tr><th>SETTING</th><th>TYPE</th><th>VALUE</th><th>DESCRIPTION</th><th>UPDATED</th><th></th></tr></thead>
        <tbody>
          {loading ? <tr><td colSpan={6} className="table-empty">Loading company settings…</td></tr> : items.length === 0 ? <tr><td colSpan={6} className="table-empty">{notice || 'No tenant settings configured.'}</td></tr> : items.map((item) => <tr key={item.id}>
            <td><strong>{item.key}</strong></td><td>{item.value_type}</td><td>{displayValue(item.value)}</td><td>{item.description || '—'}</td><td>{new Date(item.updated_at).toLocaleString()}</td><td><button className="row-action" onClick={() => beginEdit(item)}>Edit</button></td>
          </tr>)}
        </tbody>
      </table>
    </div>
    {editing && <form className="settings-editor" onSubmit={save}>
      <div className="settings-editor-header"><div><span className="section-label">EDIT SETTING</span><h3>{editing.key}</h3></div><span className="access-pill active">{editing.value_type}</span></div>
      <label>Value<textarea value={value} onChange={(event) => setValue(event.target.value)} rows={editing.value_type === 'json' ? 7 : 3} /></label>
      <label>Description<input value={description} onChange={(event) => setDescription(event.target.value)} /></label>
      <div className="settings-editor-actions"><button type="button" className="refresh-button" onClick={cancelEdit} disabled={saving}>Cancel</button><button type="submit" className="primary-action" disabled={saving}>{saving ? 'Saving…' : 'Save setting'}</button></div>
    </form>}
    {notice && <div className="inline-notice">{notice}</div>}
    <div className="boundary-note"><strong>Company Platform boundary</strong><p>These settings are tenant-scoped configuration only. Phoenix System Platform remains responsible for global platform settings, licensing, subscriptions and module activation.</p></div>
  </div>
}
