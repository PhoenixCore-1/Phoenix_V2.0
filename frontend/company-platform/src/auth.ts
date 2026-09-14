export type CoreSession = {
  authenticated: boolean
  session_id: string
  identity_id: string
  organisation_id: string
  permissions: string[]
  entitlements: string[]
}

export type PlatformDestination = {
  code: 'system' | 'company' | 'user'
  path: string
  label: string
}

export type PlatformDestinations = {
  destinations: PlatformDestination[]
  default: PlatformDestination['code']
}

type ApiEnvelope<T> = { data?: T; message?: string }

async function parseResponse<T>(response: Response): Promise<T> {
  const body = await response.json().catch(() => ({})) as ApiEnvelope<T>
  if (!response.ok || !body.data) throw new Error(body.message || `Phoenix Core request failed (${response.status}).`)
  return body.data
}

export async function getSession(): Promise<CoreSession | null> {
  const response = await fetch('/api/v1/auth/session', { credentials: 'include', headers: { Accept: 'application/json' } })
  if (response.status === 401) return null
  return parseResponse<CoreSession>(response)
}

export async function getPlatformDestinations(): Promise<PlatformDestinations> {
  const response = await fetch('/api/v1/platform/destination', { credentials: 'include', headers: { Accept: 'application/json' } })
  return parseResponse<PlatformDestinations>(response)
}

export async function login(username: string, password: string, organisationId?: string): Promise<CoreSession> {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST', credentials: 'include',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password, ...(organisationId ? { organisation_id: organisationId } : {}) }),
  })
  await parseResponse<unknown>(response)
  const session = await getSession()
  if (!session) throw new Error('Phoenix Core did not establish an authenticated session.')
  return session
}

export async function logout(): Promise<void> {
  await fetch('/api/v1/auth/logout', { method: 'POST', credentials: 'include', headers: { Accept: 'application/json', Origin: window.location.origin } })
}
