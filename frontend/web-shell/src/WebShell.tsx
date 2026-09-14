import { useEffect, useState } from 'react'
import {
  getPlatformDestinations,
  navigateToDestination,
  type PlatformDestination,
  type PlatformDestinations,
} from './platform'

export type WebShellProps = {
  currentDestination: PlatformDestination['code']
  children: React.ReactNode
}

export function WebShell({ currentDestination, children }: WebShellProps) {
  const [platforms, setPlatforms] = useState<PlatformDestinations | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    getPlatformDestinations()
      .then((value) => {
        if (active) setPlatforms(value)
      })
      .catch((reason: unknown) => {
        if (active) setError(reason instanceof Error ? reason.message : 'Unable to resolve Phoenix destinations.')
      })
    return () => {
      active = false
    }
  }, [])

  if (error) {
    return <div role="alert">Phoenix Core destination resolution failed: {error}</div>
  }

  if (!platforms) {
    return <div aria-busy="true">Loading Phoenix…</div>
  }

  return (
    <div className="phoenix-web-shell">
      <header className="phoenix-web-shell__header">
        <a className="phoenix-web-shell__brand" href={platforms.default === 'company' ? '/company' : platforms.default === 'system' ? '/system' : '/user'}>
          PHOENIX
        </a>
        <nav aria-label="Phoenix platforms">
          {platforms.destinations.map((destination) => (
            <button
              key={destination.code}
              type="button"
              aria-current={destination.code === currentDestination ? 'page' : undefined}
              onClick={() => navigateToDestination(destination)}
            >
              {destination.label}
            </button>
          ))}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  )
}
