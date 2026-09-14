import { useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getPlatformDestinations, getSession, logout, type CoreSession, type PlatformDestinations } from './auth'
import { PlatformSwitcher } from './PlatformSwitcher'
import { LoginPage } from './LoginPage'
import { Workspaces } from './Workspaces'
import { DataVisibility } from './DataVisibility'
import { Activity } from './Activity'
import { Reports } from './Reports'
import { PeopleAccess as PeopleAccessWorkspace } from './PeopleAccess'
import { CompanySettings } from './CompanySettings'
import { Compliance } from './Compliance'
import { Evidence } from './Evidence'
import { Connect } from './Connect'

type IconName = 'home' | 'people' | 'workspaces' | 'visibility' | 'activity' | 'reports' | 'settings' | 'legal' | 'evidence' | 'connect' | 'search' | 'spark' | 'bell' | 'arrow'
type NavItem = { label: string; icon: IconName }
type Company = { id: string; code: string; name: string; status: string; created_at: string }

const navigation: NavItem[] = [
  { label: 'Home', icon: 'home' }, { label: 'People & Access', icon: 'people' }, { label: 'Workspaces', icon: 'workspaces' },
  { label: 'Data Visibility', icon: 'visibility' }, { label: 'Activity', icon: 'activity' }, { label: 'Reports', icon: 'reports' }, { label: 'Compliance & Legal', icon: 'legal' }, { label: 'Evidence', icon: 'evidence' }, { label: 'Phoenix Connect', icon: 'connect' }, { label: 'Company Settings', icon: 'settings' },
]
const management = [
  { title: 'People & Access', text: 'Manage company users, memberships and company roles.', icon: 'people' as IconName },
  { title: 'Workspaces', text: 'Define the Phoenix workspaces available to company users.', icon: 'workspaces' as IconName },
  { title: 'Data Visibility', text: 'Control which company data and workspaces users can see.', icon: 'visibility' as IconName },
  { title: 'Activity', text: 'Monitor meaningful activity across the company environment.', icon: 'activity' as IconName },
  { title: 'Reports', text: 'Review company-level operational and administration reporting.', icon: 'reports' as IconName },
  { title: 'Compliance & Legal', text: 'Review company legal requirements, versions and acceptance status.', icon: 'legal' as IconName },
  { title: 'Evidence', text: 'Maintain tenant evidence records linked to Core legal documents.', icon: 'evidence' as IconName },
  { title: 'Phoenix Connect', text: 'Communicate with people inside the company through tenant-scoped conversations.', icon: 'connect' as IconName },
  { title: 'Company Settings', text: 'Manage company-level configuration available to administrators.', icon: 'settings' as IconName },
]

function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  const paths: Record<IconName, ReactNode> = {
    home: <><path d="m3 9 9-6 9 6"/><path d="M5 10v10h14V10"/><path d="M9 20v-6h6v6"/></>, people: <><circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.2 2.3-5 6-5s6 1.8 6 5"/><path d="M16 6.5a3 3 0 0 1 0 5.5M17 15c2.5.5 4 2.1 4 4"/></>, workspaces: <><rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 8h8M8 12h8M8 16h5"/></>, visibility: <><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></>, activity: <><path d="M4 19V5M4 19h17"/><path d="m7 15 4-4 3 2 5-7"/></>, reports: <><path d="M5 4h14v16H5z"/><path d="M8 8h8M8 12h8M8 16h5"/></>, settings: <><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/><circle cx="12" cy="12" r="4"/></>, legal: <><path d="M12 3v18M5 6h14M5 6l-3 6h6l-3-6ZM19 6l-3 6h6l-3-6Z"/><path d="M7 21h10"/></>, evidence: <><path d="M6 3h9l3 3v15H6z"/><path d="M9 11h6M9 15h6M9 7h4"/></>, connect: <><path d="M21 11.5a8.5 8.5 0 0 1-9 8.5 9.7 9.7 0 0 1-4.2-1L3 21l1.5-4.5A8.3 8.3 0 0 1 3 11.5 8.5 8.5 0 0 1 12 3a8.5 8.5 0 0 1 9 8.5Z"/><path d="M8 11h.01M12 11h.01M16 11h.01"/></>, search: <><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></>, spark: <><path d="m12 3 1.7 5.3L19 10l-5.3 1.7L12 17l-1.7-5.3L5 10l5.3-1.7Z"/><path d="m19 16 .7 2.3L22 19l-2.3.7Z"/></>, bell: <><path d="M18 9a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>, arrow: <><path d="M5 12h13"/><path d="m13 6 6 6-6 6"/></>,
  }
  return <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">{paths[name]}</svg>
}

async function loadCompany(): Promise<Company> {
  const response = await fetch('/api/v1/company', { credentials: 'include' })
  const body = await response.json().catch(() => ({})) as { data?: Company; message?: string }
  if (!response.ok || !body.data) throw new Error(body.message || 'Unable to load company identity.')
  return body.data
}

function App() {
  const [session, setSession] = useState<CoreSession | null>(null)
  const [destinations, setDestinations] = useState<PlatformDestinations | null>(null)
  const [checkingSession, setCheckingSession] = useState(true)
  const [destinationError, setDestinationError] = useState('')
  const [active, setActive] = useState('Home'); const [menuOpen, setMenuOpen] = useState(false); const [company, setCompany] = useState<Company | null>(null); const [companyError, setCompanyError] = useState('')
  const current = useMemo(() => navigation.find((item) => item.label === active), [active])

  async function refreshSession() {
    setCheckingSession(true)
    try {
      const currentSession = await getSession()
      setSession(currentSession)
      if (currentSession) {
        const resolved = await getPlatformDestinations()
        setDestinations(resolved)
        setDestinationError('')
      } else {
        setDestinations(null)
      }
    } catch (error) {
      setSession(null)
      setDestinations(null)
      setDestinationError(error instanceof Error ? error.message : 'Unable to resolve Phoenix destinations.')
    } finally {
      setCheckingSession(false)
    }
  }

  useEffect(() => { void refreshSession() }, [])

  useEffect(() => {
    if (!session || !destinations?.destinations.some(item => item.code === 'company')) return
    void loadCompany().then(setCompany).catch(error => setCompanyError(error instanceof Error ? error.message : 'Unable to load company identity.'))
  }, [session, destinations])

  if (checkingSession) return <div className="auth-shell"><div className="auth-loading">Connecting to Phoenix Core…</div></div>
  if (!session) return <LoginPage onAuthenticated={() => void refreshSession()} />
  const hasCompanyDestination = destinations?.destinations.some(item => item.code === 'company') ?? false
  if (destinationError || !destinations) return <div className="auth-shell"><div className="auth-card"><span className="auth-eyebrow">PHOENIX CORE</span><h1>Platform destination unavailable</h1><p className="auth-intro">{destinationError || 'Phoenix Core did not return a platform destination.'}</p><button className="auth-submit" onClick={() => { void logout().finally(() => setSession(null)) }}>Sign out</button></div></div>
  if (!hasCompanyDestination) return <div className="auth-shell"><div className="auth-card"><span className="auth-eyebrow">PHOENIX CORE</span><h1>Company Platform access required</h1><p className="auth-intro">Phoenix Core did not grant this authenticated session access to the Company Platform destination.</p><button className="auth-submit" onClick={() => { void logout().finally(() => setSession(null)) }}>Sign out</button></div></div>

  const companyName = company?.name || 'Company Platform'; const companyCode = company?.code || '—'; const companyStatus = company?.status || 'UNKNOWN'
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-mark"><span>P</span></div><span>PHOENIX</span></div><nav className="sidebar-nav" aria-label="Company Platform">{navigation.map((item) => <button key={item.label} className={`nav-item ${active === item.label ? 'active' : ''}`} onClick={() => setActive(item.label)}><Icon name={item.icon} size={15} /><span>{item.label}</span></button>)}</nav><div className="sidebar-footer">COMPANY PLATFORM <span>V1</span></div></aside><main className="main-area"><header className="topbar"><div className="topbar-title"><span className="eyebrow">PHOENIX COMPANY PLATFORM</span><h1>{companyName}</h1></div><div className="topbar-actions"><PlatformSwitcher destinations={destinations.destinations} current="company" /><button className="icon-button" aria-label="Search"><Icon name="search" /></button><button className="icon-button" aria-label="AI Assistant"><Icon name="spark" /></button><button className="icon-button" aria-label="Notifications"><Icon name="bell" /></button><button className="avatar" aria-label="Account" onClick={() => setMenuOpen(!menuOpen)}>CA</button>{menuOpen && <div className="user-popover"><strong>Company Administrator</strong><span>Company Platform · {companyCode}</span><button onClick={() => { void logout().finally(() => { setMenuOpen(false); setSession(null); setCompany(null) }) }}>Sign out</button></div>}</div></header><section className="workspace" key={active}><div className="page-header"><div><span className="section-label">COMPANY PLATFORM</span><h2>{active === 'Home' ? 'Company Overview' : active}</h2><p>{active === 'Home' ? `Administration and oversight for ${companyName}.` : `${current?.label} for the current company environment.`}</p></div><span className="status-pill"><i /> {companyStatus}</span></div>{companyError && <div className="inline-notice">{companyError}</div>}{active === 'Home' ? <><div className="summary-grid"><Summary label="COMPANY" title={companyName} meta={companyCode} /><Summary label="ADMINISTRATOR" title="Company Administrator" meta="Company Platform" /><Summary label="TENANT STATUS" title={companyStatus} meta={company?.id || 'Awaiting Core identity'} /></div><div className="section-heading"><span>ADMINISTRATION</span><h3>Company management</h3></div><div className="management-grid">{management.map((item) => <button className="management-card" key={item.title} onClick={() => setActive(item.title)}><div className="card-icon"><Icon name={item.icon} size={16} /></div><span className="card-arrow"><Icon name="arrow" size={16} /></span><div className="card-copy"><h4>{item.title}</h4><p>{item.text}</p></div></button>)}</div><div className="boundary-note"><strong>Company administration boundary</strong><p>Company Platform manages the company environment, people, access, visibility and oversight. Phoenix platform licensing, subscriptions and module activation remain outside this workspace.</p></div></> : active === 'People & Access' ? <PeopleAccessWorkspace /> : active === 'Workspaces' ? <Workspaces /> : active === 'Data Visibility' ? <DataVisibility /> : active === 'Activity' ? <Activity /> : active === 'Reports' ? <Reports /> : active === 'Company Settings' ? <CompanySettings /> : active === 'Compliance & Legal' ? <Compliance /> : active === 'Evidence' ? <Evidence /> : active === 'Phoenix Connect' ? <Connect /> : <Placeholder title={active} icon={current?.icon ?? 'settings'} />}</section></main></div>
}
function Summary({ label, title, meta }: { label: string; title: string; meta: string }) { return <div className="summary-card"><span>{label}</span><strong>{title}</strong><small>{meta}</small></div> }
function Placeholder({ title, icon }: { title: string; icon: IconName }) { return <div className="placeholder-panel"><div className="placeholder-icon"><Icon name={icon} size={22} /></div><div><span className="section-label">COMPANY WORKSPACE</span><h3>{title}</h3><p>This workspace is scaffolded and ready for its authoritative Phoenix Core API data and full interaction design.</p></div></div> }
export { App }
