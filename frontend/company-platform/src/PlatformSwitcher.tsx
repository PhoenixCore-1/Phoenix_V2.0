import type { PlatformDestination } from './auth'

const labels: Record<PlatformDestination['code'], string> = {
  system: 'System Platform',
  company: 'Company Platform',
  user: 'User Platform',
}

export function PlatformSwitcher({ destinations, current = 'company' }: { destinations: PlatformDestination[]; current?: PlatformDestination['code'] }) {
  return (
    <div className="platform-switcher" aria-label="Phoenix platform destinations">
      <span className="platform-switcher-label">PHOENIX</span>
      <select
        aria-label="Switch Phoenix platform"
        value={current}
        onChange={(event) => {
          const destination = destinations.find((item) => item.code === event.target.value)
          if (destination && destination.code !== current) window.location.assign(destination.path)
        }}
      >
        {destinations.map((destination) => (
          <option key={destination.code} value={destination.code}>{labels[destination.code] || destination.label}</option>
        ))}
      </select>
    </div>
  )
}
