import { useEffect, useState } from 'react'

type Rule = { id: string; scope_type: 'MEMBERSHIP' | 'ROLE'; membership_id: string | null; role_id: string | null; resource_code: string; visible: boolean }
type Member = { id: string; identity_id: string; status: string }
type Role = { id: string; code: string; name: string; status: string }

export function DataVisibility() {
  const [rules, setRules] = useState<Rule[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [scope, setScope] = useState<'ROLE' | 'MEMBERSHIP'>('ROLE')
  const [subject, setSubject] = useState('')
  const [resource, setResource] = useState('')
  const [visible, setVisible] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [notice, setNotice] = useState('')

  const load = async () => {
    setLoading(true); setNotice('')
    try {
      const [ruleResponse, memberResponse, roleResponse] = await Promise.all([
        fetch('/api/v1/company/visibility', { credentials: 'include' }),
        fetch('/api/v1/company/memberships', { credentials: 'include' }),
        fetch('/api/v1/company/roles', { credentials: 'include' }),
      ])
      if (!ruleResponse.ok || !memberResponse.ok || !roleResponse.ok) throw new Error('Unable to load visibility configuration')
      const ruleBody = await ruleResponse.json() as { data?: { items?: Rule[] } }
      const memberBody = await memberResponse.json() as { data?: { items?: Member[] } }
      const roleBody = await roleResponse.json() as { data?: { items?: Role[] } }
      setRules(ruleBody.data?.items ?? []); setMembers(memberBody.data?.items ?? []); setRoles(roleBody.data?.items ?? [])
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load visibility configuration.') }
    finally { setLoading(false) }
  }

  useEffect(() => { void load() }, [])

  const save = async () => {
    if (!subject || !resource.trim()) { setNotice('Select a company role or membership and enter a resource code.'); return }
    setSaving(true); setNotice('')
    try {
      const body: Record<string, unknown> = { scope_type: scope, resource_code: resource.trim(), visible }
      if (scope === 'ROLE') body.role_id = subject; else body.membership_id = subject
      const response = await fetch('/api/v1/company/visibility', { method: 'PUT', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      const result = await response.json() as { data?: Rule; message?: string }
      if (!response.ok || !result.data) throw new Error(result.message || 'Unable to save visibility rule')
      setRules((current) => { const filtered = current.filter((rule) => rule.id !== result.data!.id); return [...filtered, result.data!] })
      setNotice('Visibility rule saved in Phoenix Core.')
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to save visibility rule.') }
    finally { setSaving(false) }
  }

  const remove = async (rule: Rule) => {
    setNotice('')
    try {
      const response = await fetch(`/api/v1/company/visibility/${rule.id}`, { method: 'DELETE', credentials: 'include' })
      if (!response.ok) throw new Error('Unable to remove visibility rule')
      setRules((current) => current.filter((item) => item.id !== rule.id))
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to remove visibility rule.') }
  }

  const subjectName = (rule: Rule) => rule.scope_type === 'ROLE' ? (roles.find((role) => role.id === rule.role_id)?.name || rule.role_id) : (members.find((member) => member.id === rule.membership_id)?.identity_id || rule.membership_id)

  return <div className="people-page">
    <div className="people-toolbar"><div><span className="section-label">COMPANY DATA VISIBILITY</span><h3 style={{ margin: '5px 0' }}>Visibility policies</h3><p style={{ margin: 0, color: '#627287', fontSize: 11 }}>Restrict authorised users from seeing specific company resources. Phoenix Core permissions remain the baseline security authority.</p></div><button className="refresh-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
    <div className="access-summary"><div><span>RULES</span><strong>{rules.length}</strong></div><div><span>ROLE RULES</span><strong>{rules.filter((rule) => rule.scope_type === 'ROLE').length}</strong></div><div><span>USER RULES</span><strong>{rules.filter((rule) => rule.scope_type === 'MEMBERSHIP').length}</strong></div><div><span>SECURITY MODEL</span><strong>Core + visibility</strong></div></div>
    <div className="access-panel" style={{ display: 'block', minHeight: 0, marginBottom: 14 }}>
      <span className="section-label">ADD / UPDATE POLICY</span>
      <div style={{ display: 'grid', gridTemplateColumns: '160px 1fr 1fr auto', gap: 10, alignItems: 'end', marginTop: 12 }}>
        <label style={{ fontSize: 9, color: '#657589' }}>Scope<select value={scope} onChange={(e) => { setScope(e.target.value as 'ROLE' | 'MEMBERSHIP'); setSubject('') }} style={{ display: 'block', width: '100%', marginTop: 5, minHeight: 36, border: '1px solid #d8e0e8', borderRadius: 7, padding: '0 9px' }}><option value="ROLE">Company role</option><option value="MEMBERSHIP">Individual user</option></select></label>
        <label style={{ fontSize: 9, color: '#657589' }}>Subject<select value={subject} onChange={(e) => setSubject(e.target.value)} style={{ display: 'block', width: '100%', marginTop: 5, minHeight: 36, border: '1px solid #d8e0e8', borderRadius: 7, padding: '0 9px' }}><option value="">Select…</option>{scope === 'ROLE' ? roles.filter((role) => role.status === 'ACTIVE').map((role) => <option key={role.id} value={role.id}>{role.name} ({role.code})</option>) : members.filter((member) => member.status === 'ACTIVE').map((member) => <option key={member.id} value={member.id}>{member.identity_id}</option>)}</select></label>
        <label style={{ fontSize: 9, color: '#657589' }}>Resource code<input value={resource} onChange={(e) => setResource(e.target.value)} placeholder="e.g. customers, inventory, production" style={{ display: 'block', width: '100%', marginTop: 5, minHeight: 36, border: '1px solid #d8e0e8', borderRadius: 7, padding: '0 9px' }} /></label>
        <div><label style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 9, color: '#657589', marginBottom: 7 }}><input type="checkbox" checked={visible} onChange={(e) => setVisible(e.target.checked)} /> Explicitly visible</label><button className="primary-action" disabled={saving} onClick={() => void save()}>{saving ? 'Saving…' : 'Save rule'}</button></div>
      </div>
    </div>
    <div className="people-table-wrap"><table className="people-table"><thead><tr><th>SCOPE</th><th>SUBJECT</th><th>RESOURCE</th><th>VISIBILITY</th><th></th></tr></thead><tbody>{loading ? <tr><td colSpan={5} className="table-empty">Loading visibility rules…</td></tr> : rules.length === 0 ? <tr><td colSpan={5} className="table-empty">No explicit visibility rules configured.</td></tr> : rules.map((rule) => <tr key={rule.id}><td>{rule.scope_type === 'ROLE' ? 'ROLE' : 'USER'}</td><td>{subjectName(rule)}</td><td><strong>{rule.resource_code}</strong></td><td><span className={`access-pill ${rule.visible ? 'active' : 'removed'}`}>{rule.visible ? 'VISIBLE' : 'HIDDEN'}</span></td><td><button className="row-action" onClick={() => void remove(rule)}>Remove</button></td></tr>)}</tbody></table></div>
    {notice && <div className="inline-notice">{notice}</div>}
  </div>
}
