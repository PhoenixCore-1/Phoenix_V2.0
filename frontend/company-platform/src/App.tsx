import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { Workspaces } from './Workspaces'
import { DataVisibility } from './DataVisibility'
import { Activity } from './Activity'
import { CompanySettings } from './CompanySettings'
import { Compliance } from './Compliance'

type IconName = 'home' | 'people' | 'workspaces' | 'visibility' | 'activity' | 'reports' | 'settings' | 'legal' | 'search' | 'spark' | 'bell' | 'arrow'
type NavItem = { label: string; icon: IconName }
type UserRow = { id: string; display_name: string; username: string; user_status: string; membership_status: string }

const navigation: NavItem[] = [
  { label: 'Home', icon: 'home' }, { label: 'People & Access', icon: 'people' }, { label: 'Workspaces', icon: 'workspaces' },
  { label: 'Data Visibility', icon: 'visibility' }, { label: 'Activity', icon: 'activity' }, { label: 'Reports', icon: 'reports' }, { label: 'Compliance & Legal', icon: 'legal' }, { label: 'Company Settings', icon: 'settings' },
]
const management = [
  { title: 'People & Access', text: 'Manage company users, memberships and company roles.', icon: 'people' as IconName },
  { title: 'Workspaces', text: 'Define the Phoenix workspaces available to company users.', icon: 'workspaces' as IconName },
  { title: 'Data Visibility', text: 'Control which company data and workspaces users can see.', icon: 'visibility' as IconName },
  { title: 'Activity', text: 'Monitor meaningful activity across the company environment.', icon: 'activity' as IconName },
  { title: 'Reports', text: 'Review company-level operational and administration reporting.', icon: 'reports' as IconName },
  { title: 'Compliance & Legal', text: 'Review company legal requirements, versions and acceptance status.', icon: 'legal' as IconName },
  { title: 'Company Settings', text: 'Manage company-level configuration available to administrators.', icon: 'settings' as IconName },
]

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    home: <><path d="m3 9 9-6 9 6"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></>,
    people: <><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.2 2.3-5 6-5s6 1.8 6 5"/><path d="M16 6.5a3 3 0 0 1 0 5.5M17 15c2.5.5 4 2.1 4 4"/></>,
    workspaces: <><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></>,
    visibility: <><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></>,
    activity: <><path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 2 5-7"/></>,
    reports: <><path d="M5 4h14v16H5z"/><path d="M8 8h8M8 12h8M8 16h5"/></>,
    settings: <><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/><circle cx="12" cy="12" r="4"/></>,
    legal: <><path d="M12 3v18M5 6h14M5 6l-3 6h6l-3-6ZM19 6l-3 6h6l-3-6Z"/><path d="M7 21h10"/></>,
    search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>,
    spark: <><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7Z"/></>,
    bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
    arrow: <><path d="M5 12h13"/><path d="m13 6 6 6-6 6"/></>,
  }
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>
}

function PeopleAccess() {
  const [query, setQuery] = useState(''); const [status, setStatus] = useState('ALL'); const [users, setUsers] = useState<UserRow[]>([]); const [loading, setLoading] = useState(false); const [notice, setNotice] = useState('')
  const loadUsers = async () => { setLoading(true); setNotice(''); try { const response = await fetch('/api/v1/company/users', { credentials: 'include' }); if (!response.ok) throw new Error('Core API unavailable'); const body = await response.json() as { data?: { items?: UserRow[] } }; setUsers(body.data?.items ?? []) } catch { setNotice('Connect this workspace to an authenticated Phoenix Core session to load company users.') } finally { setLoading(false) } }
  useEffect(() => { void loadUsers() }, [])
  const filtered = useMemo(() => users.filter((user) => `${user.display_name} ${user.username}`.toLowerCase().includes(query.toLowerCase()) && (status === 'ALL' || user.membership_status === status)), [users, query, status])
  return <div className="people-page"><div className="people-toolbar"><div><span className="section-label">PEOPLE & ACCESS</span><h3 style={{ margin: '5px 0' }}>Company users</h3></div><button className="primary-action" onClick={() => setNotice('User provisioning is controlled by the Phoenix Core company-user boundary.')}>+ Add user</button></div><div className="access-summary"><div><span>ACTIVE USERS</span><strong>{users.filter((u) => u.membership_status === 'ACTIVE').length}</strong></div><div><span>SUSPENDED</span><strong>{users.filter((u) => u.membership_status === 'SUSPENDED').length}</strong></div><div><span>TENANT ACCESS</span><strong>Core</strong></div><div><span>AUTHORITY</span><strong>Core controlled</strong></div></div><div className="people-controls"><label className="search-field"><Icon name="search" size={15} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search people..." /></label><select value={status} onChange={(e) => setStatus(e.target.value)}><option value="ALL">All statuses</option><option value="ACTIVE">Active</option><option value="SUSPENDED">Suspended</option><option value="REMOVED">Removed</option></select><button className="refresh-button" onClick={() => void loadUsers()}>Refresh</button></div><div className="people-table-wrap"><table className="people-table"><thead><tr><th>PERSON</th><th>USERNAME</th><th>ACCESS</th><th>USER STATUS</th><th></th></tr></thead><tbody>{loading ? <tr><td colSpan={5} className="table-empty">Loading company users…</td></tr> : filtered.length === 0 ? <tr><td colSpan={5} className="table-empty">{notice || 'No company users returned from Phoenix Core.'}</td></tr> : filtered.map((user) => <tr key={user.id}><td><div className="person-cell"><span className="person-avatar">{user.display_name.slice(0, 2).toUpperCase()}</span><strong>{user.display_name}</strong></div></td><td>{user.username}</td><td><span className={`access-pill ${user.membership_status.toLowerCase()}`}>{user.membership_status}</span></td><td>{user.user_status}</td><td><button className="row-action" onClick={() => setNotice(`Selected ${user.display_name}`)}>View</button></td></tr>)}</tbody></table></div>{notice && <div className="inline-notice">{notice}</div>}</div>
}

function App() {
  const [active, setActive] = useState('Home'); const [menuOpen, setMenuOpen] = useState(false); const current = useMemo(() => navigation.find((item) => item.label === active), [active])
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-mark"><span>P</span></div><span>PHOENIX</span></div><nav className="sidebar-nav" aria-label="Company Platform">{navigation.map((item) => <button key={item.label} className={`nav-item ${active === item.label ? 'active' : ''}`} onClick={() => setActive(item.label)}><Icon name={item.icon} size={15} /><span>{item.label}</span></button>)}</nav><div className="sidebar-footer">COMPANY PLATFORM <span>V1</span></div></aside><main className="main-area"><header className="topbar"><div className="topbar-title"><span className="eyebrow">PHOENIX PLATFORM</span><h1>Company Platform</h1></div><div className="topbar-actions"><button className="icon-button" aria-label="Search"><Icon name="search" /></button><button className="icon-button" aria-label="AI Assistant"><Icon name="spark" /></button><button className="icon-button" aria-label="Notifications"><Icon name="bell" /></button><button className="avatar" aria-label="Account" onClick={() => setMenuOpen(!menuOpen)}>CA</button>{menuOpen && <div className="user-popover"><strong>Company Administrator</strong><span>Company Platform</span><button onClick={() => setMenuOpen(false)}>Close</button></div>}</div></header><section className="workspace" key={active}><div className="page-header"><div><span className="section-label">COMPANY PLATFORM</span><h2>{active === 'Home' ? 'Company Overview' : active}</h2><p>{active === 'Home' ? 'Administration and oversight for Phoenix Development Company.' : `${current?.label} for the current company environment.`}</p></div><span className="status-pill"><i /> ACTIVE</span></div>{active === 'Home' ? <><div className="summary-grid"><Summary label="COMPANY" title="Phoenix Development Company" meta="DEVCO" /><Summary label="ADMINISTRATOR" title="Company Administrator" meta="company.admin" /><Summary label="ACTIVE MODULES" title="1" meta="Modules available to this company" /></div><div className="section-heading"><span>ADMINISTRATION</span><h3>Company management</h3></div><div className="management-grid">{management.map((item) => <button className="management-card" key={item.title} onClick={() => setActive(item.title)}><div className="card-icon"><Icon name={item.icon} size={16} /></div><span className="card-arrow"><Icon name="arrow" size={16} /></span><div className="card-copy"><h4>{item.title}</h4><p>{item.text}</p></div></button>)}</div><div className="boundary-note"><strong>Company administration boundary</strong><p>Company Platform manages the company environment, people, access, visibility and oversight. Phoenix platform licensing, subscriptions and module activation remain outside this workspace.</p></div></> : active === 'People & Access' ? <PeopleAccess /> : active === 'Workspaces' ? <Workspaces /> : active === 'Data Visibility' ? <DataVisibility /> : active === 'Activity' ? <Activity /> : active === 'Company Settings' ? <CompanySettings /> : active === 'Compliance & Legal' ? <Compliance /> : <Placeholder title={active} icon={current?.icon ?? 'settings'} />}</section></main></div>
}
function Summary({ label, title, meta }: { label: string; title: string; meta: string }) { return <div className="summary-card"><span>{label}</span><strong>{title}</strong><small>{meta}</small></div> }
function Placeholder({ title, icon }: { title: string; icon: IconName }) { return <div className="placeholder-panel"><div className="placeholder-icon"><Icon name={icon} size={22} /></div><div><span className="section-label">COMPANY WORKSPACE</span><h3>{title}</h3><p>This workspace is scaffolded and ready for its authoritative Phoenix Core API data and full interaction design.</p></div></div> }
export { App }
