import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import axios from 'axios'
import { supabase } from '../lib/supabase'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const countries = ['India', 'UAE', 'UK', 'US', 'Singapore', 'Australia', 'Other']

const pricing = [
  { id: 'starter', name: 'Starter', price: '₹2,999', period: '/mo', blurb: 'Up to 10 active clients' },
  { id: 'professional', name: 'Professional', price: '₹7,999', period: '/mo', blurb: 'Up to 50 active clients' },
  { id: 'agency', name: 'Agency', price: '₹19,999', period: '/mo', blurb: 'Unlimited clients (fair use)' },
]

function slugify(name: string) {
  return (
    name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '') || 'firm'
  )
}

export default function RegisterFirm() {
  const nav = useNavigate()
  const [step, setStep] = useState(1)
  const [busy, setBusy] = useState(false)

  const [firm_name, setFirmName] = useState('')
  const [slug, setSlug] = useState('')
  const [country, setCountry] = useState('India')
  const [whatsapp_number, setWhatsapp] = useState('')

  const [owner_name, setOwnerName] = useState('')
  const [owner_email, setOwnerEmail] = useState('')
  const [password, setPassword] = useState('')
  const [password2, setPassword2] = useState('')

  const [plan, setPlan] = useState('starter')

  const previewSlug = useMemo(() => slug || slugify(firm_name), [slug, firm_name])
  const portalPreview = `${window.location.origin}/portal/${previewSlug}/…`

  async function submit() {
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters')
      return
    }
    if (password !== password2) {
      toast.error('Passwords do not match')
      return
    }
    setBusy(true)
    try {
      await axios.post(`${API}/api/auth/register-firm`, {
        firm_name,
        slug: previewSlug,
        country,
        whatsapp_number: whatsapp_number || null,
        plan,
        owner_email,
        owner_name,
        password,
      })
      const { error } = await supabase.auth.signInWithPassword({ email: owner_email, password })
      if (error) throw error
      toast.success(`Welcome to CPAOS, ${firm_name}! Let's add your first client.`)
      nav('/dashboard')
    } catch (e: any) {
      const d = e?.response?.data?.detail
      toast.error(typeof d === 'string' ? d : e?.message || 'Registration failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-screen noise flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 shadow-xl">
        <h1 className="font-display text-2xl font-semibold">Create your firm</h1>
        <p className="text-sm text-slate-400 mt-1">Step {step} of 3</p>

        {step === 1 && (
          <div className="mt-6 space-y-3">
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="Firm name *"
              value={firm_name}
              onChange={(e) => {
                setFirmName(e.target.value)
                if (!slug) setSlug(slugify(e.target.value))
              }}
            />
            <div>
              <input
                className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                placeholder="Firm slug (URL-safe)"
                value={slug || slugify(firm_name)}
                onChange={(e) => setSlug(slugify(e.target.value))}
              />
              <p className="text-xs text-slate-500 mt-1 break-all">Your portal URL will be: {portalPreview}</p>
            </div>
            <div>
              <div className="text-xs text-slate-400 mb-1">Primary country</div>
              <select
                className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
              >
                {countries.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="WhatsApp business number (optional)"
              value={whatsapp_number}
              onChange={(e) => setWhatsapp(e.target.value)}
            />
            <button
              type="button"
              className="w-full rounded-lg bg-primary py-2 text-sm font-semibold text-white"
              onClick={() => firm_name && setStep(2)}
              disabled={!firm_name}
            >
              Next
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="mt-6 space-y-3">
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="Full name *"
              value={owner_name}
              onChange={(e) => setOwnerName(e.target.value)}
            />
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="Email *"
              type="email"
              value={owner_email}
              onChange={(e) => setOwnerEmail(e.target.value)}
            />
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="Password (min 8) *"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <input
              className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
              placeholder="Confirm password *"
              type="password"
              value={password2}
              onChange={(e) => setPassword2(e.target.value)}
            />
            <div className="flex gap-2">
              <button type="button" className="flex-1 rounded-lg border border-border py-2 text-sm" onClick={() => setStep(1)}>
                Back
              </button>
              <button
                type="button"
                className="flex-1 rounded-lg bg-primary py-2 text-sm font-semibold text-white"
                onClick={() => owner_name && owner_email && password && setStep(3)}
                disabled={!owner_name || !owner_email || !password}
              >
                Next
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="mt-6 space-y-3">
            <p className="text-xs text-slate-400">Start with Starter — upgrade anytime (pre-selected).</p>
            <div className="grid gap-3">
              {pricing.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setPlan(p.id)}
                  className={`text-left rounded-xl border p-4 transition-colors ${
                    plan === p.id ? 'border-primary bg-primary/10' : 'border-border bg-bg'
                  }`}
                >
                  <div className="font-semibold">
                    {p.name}{' '}
                    <span className="text-primary">
                      {p.price}
                      <span className="text-slate-500 text-sm">{p.period}</span>
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 mt-1">{p.blurb}</div>
                </button>
              ))}
            </div>
            <div className="flex gap-2 pt-2">
              <button type="button" className="flex-1 rounded-lg border border-border py-2 text-sm" onClick={() => setStep(2)}>
                Back
              </button>
              <button
                type="button"
                disabled={busy}
                className="flex-1 rounded-lg bg-primary py-2 text-sm font-semibold text-white disabled:opacity-50"
                onClick={submit}
              >
                {busy ? 'Creating…' : 'Create firm account'}
              </button>
            </div>
          </div>
        )}

        <p className="text-xs text-slate-500 mt-6">
          Already have an account?{' '}
          <Link className="text-primary" to="/login">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
