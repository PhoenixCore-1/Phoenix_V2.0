export type PlatformDestination = {
  code: 'system' | 'company' | 'user'
  path: string
  label: string
}

export type PlatformDestinations = {
  destinations: PlatformDestination[]
  default: PlatformDestination['code']
}

type ApiEnvelope<T> = {
  data: T
  request_id?: string
}

async function parseResponse<T>(response: Response): Promise<T> {
  const body = (await response.json()) as ApiEnvelope<T> | T
  if (!response.ok) {
    const message = typeof body === 'object' && body !== null && 'message' in body
      ? String((body as { message?: unknown }).message)
      : `Phoenix Core request failed (${response.status})`
    throw new Error(message)
  }
  return (typeof body === 'object' && body !== null && 'data' in body)
    ? (body as ApiEnvelope<T>).data
    : (body as T)
}

/**
 * Shared Web Shell adapter. Core's secure session cookie is the only browser
 * authentication transport; destination access is resolved by Core.
 */
export async function getPlatformDestinations(): Promise<PlatformDestinations> {
  const response = await fetch('/api/v1/platform/destination', {
    credentials: 'include',
    headers: { Accept: 'application/json' },
  })
  return parseResponse<PlatformDestinations>(response)
}

export function navigateToDestination(destination: PlatformDestination): void {
  window.location.assign(destination.path)
}
