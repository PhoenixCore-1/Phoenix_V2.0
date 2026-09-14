import { FormEvent, useEffect, useMemo, useState } from 'react'

type User = { id: string; identity_id: string; username: string; display_name: string; user_status: string; membership_id: string; membership_status: string; created_at: string }
type Role = { id: string; organisation_id: string; code: string; name: string; scope: string; status: string; created_at: string }
type Permission = { id: string; code: string; name: string; created_at: string }

type ApiBody<T> = { data?: { items?: T[]; item?: T }; error?: { message?: string } }

async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { credentials: 'include', ...init, headers: { ...(init?.body ? { 'Content-Type': 'application/json' } : {}), ...(init?.headers ?? {}) } })
  const body = await response.json().catch(() => ({})) as ApiBody<T>
  if (!response.ok) throw new Error(body.error?.message || 'Phoenix Core request failed.')
  return body as T
}

export function PeopleAccess() {
  const [tab, setTab] = useState<'people' | 'roles'>('people')
  const [users, setUsers] = useState<User[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [rolePermissions, setRolePermissions] = useState<Permission[]>([])
  const [selectedRoleId, setSelectedRoleId] = useState('')
  const [loading, setLoading] = useState(true)
  const [permissionsLoading, setPermissionsLoading] = useState(false)
  const [notice, setNotice] = useState('')
  const [query, setQuery] = useState('')
  const [status, setStatus] = useState('ALL')
  const [showUserForm, setShowUserForm] = useState(false)
  const [showRoleForm, setShowRoleForm] = useState(false)
  const [userForm, setUserForm] = useState({ username: '', display_name: '', password: '' })
  const [roleForm, setRoleForm] = useState({ code: '', name: '' })
  const [saving, setSaving] = useState(false)

  const loadUsers = async () => { const body = await api<{ data?: { items?: User[] } }>('/api/v1/company/users'); setUsers(body.data?.items ?? []) }
  const loadRoles = async () => { const body = await api<{ data?: { items?: Role[] } }>('/api/v1/company/roles'); setRoles(body.data?.items ?? []) }
  const loadPermissions = async () => { const body = await api<{ data?: { items?: Permission[] } }>('/api/v1/company/permissions'); setPermissions(body.data?.items ?? []) }
  const loadRolePermissions = async (roleId: string) => {
    if (!roleId) { setRolePermissions([]); return }
    setPermissionsLoading(true); setNotice('')
    try { const body = await api<{ data?: { items?: Permission[] } }>(`/api/v1/company/roles/${roleId}/permissions`); setRolePermissions(body.data?.items ?? []) }
    catch (error) { setRolePermissions([]); setNotice(error instanceof Error ? error.message : 'Unable to load role permissions.') }
    finally { setPermissionsLoading(false) }
  }
  const load = async () => { setLoading(true); setNotice(''); try { await Promise.all([loadUsers(), loadRoles(), loadPermissions()]) } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to load People & Access.') } finally { setLoading(false) } }
  useEffect(() => { void load() }, [])
  useEffect(() => { if (selectedRoleId) void loadRolePermissions(selectedRoleId); else setRolePermissions([]) }, [selectedRoleId])

  const filteredUsers = useMemo(() => users.filter((user) => `${user.display_name} ${user.username}`.toLowerCase().includes(query.toLowerCase()) && (status === 'ALL' || user.membership_status === status)), [users, query, status])
  const selectedRole = roles.find((role) => role.id === selectedRoleId)
  const assignedPermissionIds = useMemo(() => new Set(rolePermissions.map((permission) => permission.id)), [rolePermissions])

  const createUser = async (event: FormEvent) => {
    event.preventDefault(); setSaving(true); setNotice('')
    try { await api('/api/v1/company/users', { method: 'POST', body: JSON.stringify(userForm) }); setUserForm({ username: '', display_name: '', password: '' }); setShowUserForm(false); await loadUsers(); setNotice('Company user created in Phoenix Core.') }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to create company user.') } finally { setSaving(false) }
  }

  const updateUser = async (user: User) => {
    const displayName = window.prompt('Display name', user.display_name); if (displayName === null) return
    const username = window.prompt('Username', user.username); if (username === null) return
    setSaving(true); setNotice('')
    try { await api(`/api/v1/company/users/${user.id}`, { method: 'PATCH', body: JSON.stringify({ display_name: displayName, username }) }); await loadUsers(); setNotice(`Updated ${displayName}.`) }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to update user.') } finally { setSaving(false) }
  }

  const membershipAction = async (user: User, action: 'suspend' | 'restore' | 'remove') => {
    const labels = { suspend: 'Suspend', restore: 'Restore', remove: 'Remove' }; if (!window.confirm(`${labels[action]} ${user.display_name}?`)) return
    setSaving(true); setNotice('')
    try { await api(`/api/v1/company/memberships/${user.membership_id}/${action}`, { method: 'POST' }); await loadUsers(); setNotice(`${labels[action]}d ${user.display_name}.`) }
    catch (error) { setNotice(error instanceof Error ? error.message : `Unable to ${action} membership.`) } finally { setSaving(false) }
  }

  const createRole = async (event: FormEvent) => {
    event.preventDefault(); setSaving(true); setNotice('')
    try { await api('/api/v1/company/roles', { method: 'POST', body: JSON.stringify(roleForm) }); setRoleForm({ code: '', name: '' }); setShowRoleForm(false); await loadRoles(); setNotice('Company role created in Phoenix Core.') }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to create role.') } finally { setSaving(false) }
  }

  const editRole = async (role: Role) => {
    const name = window.prompt('Role name', role.name); if (name === null) return
    const code = window.prompt('Role code', role.code); if (code === null) return
    setSaving(true); setNotice('')
    try { await api(`/api/v1/company/roles/${role.id}`, { method: 'PATCH', body: JSON.stringify({ name, code }) }); await loadRoles(); setNotice(`Updated ${name}.`) }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to update role.') } finally { setSaving(false) }
  }

  const toggleRole = async (role: Role) => {
    const action = role.status === 'ACTIVE' ? 'disable' : 'enable'; if (!window.confirm(`${action === 'disable' ? 'Disable' : 'Enable'} ${role.name}?`)) return
    setSaving(true); setNotice('')
    try { await api(`/api/v1/company/roles/${role.id}/${action}`, { method: 'POST' }); await loadRoles(); setNotice(`${role.name} is now ${action === 'disable' ? 'disabled' : 'active'}.`) }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to change role status.') } finally { setSaving(false) }
  }

  const togglePermission = async (permission: Permission) => {
    if (!selectedRoleId) return
    const assigned = assignedPermissionIds.has(permission.id)
    setSaving(true); setNotice('')
    try {
      await api(`/api/v1/company/roles/${selectedRoleId}/permissions/${permission.id}`, { method: assigned ? 'DELETE' : 'POST' })
      await loadRolePermissions(selectedRoleId)
      setNotice(`${permission.name} ${assigned ? 'removed from' : 'granted to'} ${selectedRole?.name || 'role'}.`)
    } catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to update role permission.') }
    finally { setSaving(false) }
  }

  return <div className="people-page">
    <div className="people-toolbar"><div><span className="section-label">PEOPLE & ACCESS</span><h3 style={{ margin: '5px 0' }}>{tab === 'people' ? 'Company users' : 'Company roles'}</h3></div><div style={{ display: 'flex', gap: 8 }}>{tab === 'people' ? <button className="primary-action" onClick={() => setShowUserForm(true)}>+ Add user</button> : <button className="primary-action" onClick={() => setShowRoleForm(true)}>+ Add role</button>}<button className="refresh-button" onClick={() => void load()} disabled={loading || saving}>Refresh</button></div></div>
    <div className="people-tabs"><button className={tab === 'people' ? 'active' : ''} onClick={() => setTab('people')}>People</button><button className={tab === 'roles' ? 'active' : ''} onClick={() => setTab('roles')}>Roles & permissions</button></div>
    {tab === 'people' ? <>
      <div className="access-summary"><div><span>ACTIVE USERS</span><strong>{users.filter((u) => u.membership_status === 'ACTIVE').length}</strong></div><div><span>SUSPENDED</span><strong>{users.filter((u) => u.membership_status === 'SUSPENDED').length}</strong></div><div><span>TENANT ACCESS</span><strong>Core</strong></div><div><span>AUTHORITY</span><strong>Core controlled</strong></div></div>
      <div className="people-controls"><label className="search-field"><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search people..." /></label><select value={status} onChange={(e) => setStatus(e.target.value)}><option value="ALL">All statuses</option><option value="ACTIVE">Active</option><option value="SUSPENDED">Suspended</option><option value="REMOVED">Removed</option></select></div>
      <div className="people-table-wrap"><table className="people-table"><thead><tr><th>PERSON</th><th>USERNAME</th><th>ACCESS</th><th>USER STATUS</th><th>ACTIONS</th></tr></thead><tbody>{loading ? <tr><td colSpan={5} className="table-empty">Loading company users…</td></tr> : filteredUsers.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No company users returned from Phoenix Core.'}</td></tr> : filteredUsers.map((user) => <tr key={user.id}><td><div className="person-cell"><span className="person-avatar">{user.display_name.slice(0, 2).toUpperCase()}</span><strong>{user.display_name}</strong></div></td><td>{user.username}</td><td><span className={`access-pill ${user.membership_status.toLowerCase()}`}>{user.membership_status}</span></td><td>{user.user_status}</td><td><div className="row-actions"><button className="row-action" onClick={() => void updateUser(user)} disabled={saving}>Edit</button>{user.membership_status === 'ACTIVE' ? <button className="row-action" onClick={() => void membershipAction(user, 'suspend')} disabled={saving}>Suspend</button> : user.membership_status === 'SUSPENDED' ? <button className="row-action" onClick={() => void membershipAction(user, 'restore')} disabled={saving}>Restore</button> : null}{user.membership_status !== 'REMOVED' && <button className="row-action danger" onClick={() => void membershipAction(user, 'remove')} disabled={saving}>Remove</button>}</div></td></tr>)}</tbody></table></div>
      {showUserForm && <form className="settings-editor" onSubmit={createUser}><div className="settings-editor-header"><div><span className="section-label">NEW COMPANY USER</span><h3>Create user</h3></div></div><label>Display name<input required value={userForm.display_name} onChange={(e) => setUserForm({ ...userForm, display_name: e.target.value })} /></label><label>Username<input required value={userForm.username} onChange={(e) => setUserForm({ ...userForm, username: e.target.value })} /></label><label>Initial password<input required type="password" value={userForm.password} onChange={(e) => setUserForm({ ...userForm, password: e.target.value })} /></label><div className="settings-editor-actions"><button type="button" className="refresh-button" onClick={() => setShowUserForm(false)}>Cancel</button><button type="submit" className="primary-action" disabled={saving}>{saving ? 'Creating…' : 'Create user'}</button></div></form>}
    </> : <>
      <div className="access-summary"><div><span>ROLES</span><strong>{roles.length}</strong></div><div><span>ACTIVE</span><strong>{roles.filter((r) => r.status === 'ACTIVE').length}</strong></div><div><span>PERMISSIONS</span><strong>{permissions.length}</strong></div><div><span>AUTHORITY</span><strong>Core controlled</strong></div></div>
      <div className="people-table-wrap"><table className="people-table"><thead><tr><th>ROLE</th><th>CODE</th><th>SCOPE</th><th>STATUS</th><th>ACTIONS</th></tr></thead><tbody>{roles.length === 0 ? <tr><td colSpan={5} className="table-empty">No company roles returned from Phoenix Core.</td></tr> : roles.map((role) => <tr key={role.id}><td><strong>{role.name}</strong></td><td>{role.code}</td><td>{role.scope}</td><td><span className={`access-pill ${role.status.toLowerCase()}`}>{role.status}</span></td><td><div className="row-actions"><button className={`row-action ${selectedRoleId === role.id ? 'active' : ''}`} onClick={() => setSelectedRoleId(selectedRoleId === role.id ? '' : role.id)} disabled={saving}>Permissions</button><button className="row-action" onClick={() => void editRole(role)} disabled={saving}>Edit</button><button className="row-action" onClick={() => void toggleRole(role)} disabled={saving}>{role.status === 'ACTIVE' ? 'Disable' : 'Enable'}</button></div></td></tr>)}</tbody></table></div>
      {selectedRole && <div className="access-panel" style={{ display: 'block', minHeight: 0, marginTop: 14 }}><div className="people-toolbar" style={{ padding: 0, marginBottom: 12 }}><div><span className="section-label">ROLE PERMISSIONS</span><h3 style={{ margin: '5px 0' }}>{selectedRole.name}</h3><p style={{ margin: 0, color: '#627287', fontSize: 11 }}>Grant or revoke tenant permissions through Phoenix Core. These changes remain subject to server-side authorization and audit.</p></div><span className="access-pill active">{rolePermissions.length} ASSIGNED</span></div>{permissionsLoading ? <p>Loading permissions…</p> : permissions.length === 0 ? <p>No permissions are available from Phoenix Core.</p> : <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: 8 }}>{permissions.map((permission) => { const assigned = assignedPermissionIds.has(permission.id); return <button key={permission.id} type="button" onClick={() => void togglePermission(permission)} disabled={saving} style={{ textAlign: 'left', border: '1px solid #d8e0e8', borderRadius: 8, padding: '10px 12px', background: assigned ? '#eef7ff' : '#fff', cursor: saving ? 'wait' : 'pointer' }}><strong style={{ display: 'block', fontSize: 12 }}>{permission.name}</strong><span style={{ fontSize: 10, color: '#627287' }}>{permission.code}</span><span className={`access-pill ${assigned ? 'active' : 'suspended'}`} style={{ float: 'right', marginTop: -20 }}>{assigned ? 'GRANTED' : 'NOT GRANTED'}</span></button> })}</div>}</div>}
      {showRoleForm && <form className="settings-editor" onSubmit={createRole}><div className="settings-editor-header"><div><span className="section-label">NEW COMPANY ROLE</span><h3>Create role</h3></div></div><label>Role name<input required value={roleForm.name} onChange={(e) => setRoleForm({ ...roleForm, name: e.target.value })} /></label><label>Role code<input required value={roleForm.code} onChange={(e) => setRoleForm({ ...roleForm, code: e.target.value })} /></label><div className="settings-editor-actions"><button type="button" className="refresh-button" onClick={() => setShowRoleForm(false)}>Cancel</button><button type="submit" className="primary-action" disabled={saving}>{saving ? 'Creating…' : 'Create role'}</button></div></form>}
    </>}
    {notice && <div className="inline-notice">{notice}</div>}
    <div className="boundary-note"><strong>Company Platform boundary</strong><p>User, membership and company-role changes are sent to Phoenix Core for authorization and audit. Phoenix System Platform remains responsible for licensing, subscriptions and module activation.</p></div>
  </div>
}
