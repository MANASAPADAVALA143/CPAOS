import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

export default function Login() {
  const nav = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  /** Block browser autofill until the user focuses a field (then they can type normally). */
  const [suppressAutofill, setSuppressAutofill] = useState(true)

  async function onPasswordLogin(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    setBusy(false)
    if (error) alert(error.message)
    else nav('/dashboard')
  }

  async function onMagicLink() {
    setBusy(true)
    const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin } })
    setBusy(false)
    if (error) alert(error.message)
    else alert('Check your email for the login link.')
  }

  return (
    <div className="min-h-screen noise flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-8 shadow-xl">
        <h1 className="font-display text-2xl font-semibold">CPAOS</h1>
        <p className="text-sm text-slate-400 mt-1">Sign in to your firm workspace</p>
        <form className="mt-6 space-y-3" onSubmit={onPasswordLogin} autoComplete="off">
          <input
            className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
            placeholder="Email"
            name="cpaos-email"
            id="cpaos-email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onFocus={() => setSuppressAutofill(false)}
            type="email"
            autoComplete="off"
            readOnly={suppressAutofill}
            required
          />
          <input
            className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
            placeholder="Password"
            name="cpaos-password"
            id="cpaos-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => setSuppressAutofill(false)}
            type="password"
            autoComplete="new-password"
            readOnly={suppressAutofill}
          />
          <button
            disabled={busy}
            className="w-full rounded-lg bg-primary py-2 text-sm font-semibold text-white disabled:opacity-50"
            type="submit"
          >
            Sign in
          </button>
        </form>
        <button
          type="button"
          disabled={busy || !email}
          onClick={onMagicLink}
          className="mt-3 w-full rounded-lg border border-border py-2 text-sm text-slate-200 disabled:opacity-50"
        >
          Send me a login link
        </button>
        <p className="text-xs text-slate-500 mt-4">
          New firm?{' '}
          <Link className="text-primary" to="/register">
            Create your account
          </Link>
        </p>
        <Link className="text-xs text-slate-500 block mt-2" to="/">
          ← Back to dashboard
        </Link>
        <Link className="text-xs text-primary block mt-3" to="/portal/demo-accounting/22222222-2222-2222-2222-222222222222">
          Open public portal demo
        </Link>
      </div>
    </div>
  )
}
