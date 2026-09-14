import { FormEvent, useState } from 'react'
import { login } from './auth'

type Props = { onAuthenticated: () => void }

export function LoginPage({ onAuthenticated }: Props) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setBusy(true)
    try {
      await login(username.trim(), password)
      onAuthenticated()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Unable to sign in to Phoenix Core.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-brand"><div className="brand-mark"><span>P</span></div><span>PHOENIX</span></div>
        <span className="auth-eyebrow">PHOENIX CORE</span>
        <h1>Sign in to Phoenix</h1>
        <p className="auth-intro">Use your Phoenix Core account to continue to the Company Platform.</p>
        <form onSubmit={submit} className="auth-form">
          <label>Username<input autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required /></label>
          <label>Password<input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
          {error && <div className="auth-error" role="alert">{error}</div>}
          <button className="auth-submit" type="submit" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
        </form>
        <div className="auth-boundary">Authentication, sessions, identity and organisation access are provided by Phoenix Core. Company Platform does not maintain a separate login.</div>
      </div>
    </div>
  )
}
