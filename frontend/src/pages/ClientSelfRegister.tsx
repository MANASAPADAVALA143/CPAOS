import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import axios from 'axios'
import { CountryFlag } from '../components/CountryFlag'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8001'

const countries = ['India', 'UAE', 'UK', 'US', 'Singapore', 'Australia', 'Other']

const entityOptions: Record<string, string[]> = {
  India: ['individual', 'sole_proprietor', 'partnership', 'llp', 'private_limited', 'public_limited', 'trust', 'other'],
  UAE: ['individual', 'sole_proprietor', 'private_limited'],
  UK: ['individual', 'sole_trader', 'private_limited', 'llp'],
  US: ['individual', 'sole_proprietor', 'llc', 's_corp', 'c_corp'],
  Singapore: ['private_limited'],
  Australia: ['private_limited'],
  Other: ['other'],
}

type FirmPublic = {
  firm_name: string
  primary_color: string
  logo_url: string | null
  whatsapp_number: string | null
}

export default function ClientSelfRegister() {
  const { firmSlug } = useParams<{ firmSlug: string }>()
  const [firm, setFirm] = useState<FirmPublic | null>(null)
  const [firmLoading, setFirmLoading] = useState(true)
  const [firmError, setFirmError] = useState<string | null>(null)
  const [logoFailed, setLogoFailed] = useState(false)

  const [done, setDone] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const [client_name, setClientName] = useState('')
  const [business_name, setBusinessName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')

  const [country, setCountry] = useState('India')
  const [entity_type, setEntityType] = useState('private_limited')
  const [services, setServices] = useState<string[]>(['bookkeeping', 'tax'])
  const [financial_year_end, setFye] = useState('')

  const entities = useMemo(() => entityOptions[country] || entityOptions.Other, [country])

  useEffect(() => {
    if (!firmSlug) return
    let cancelled = false
    setFirmLoading(true)
    setFirmError(null)
    fetch(`${API}/api/portal/${firmSlug}/info`)
      .then(async (r) => {
        if (r.status === 404) throw new Error('not_found')
        if (!r.ok) throw new Error('load_failed')
        return r.json()
      })
      .then((data) => {
        if (!cancelled) {
          setFirm({
            firm_name: data.firm_name,
            primary_color: data.primary_color || '#2563EB',
            logo_url: data.logo_url ?? null,
            whatsapp_number: data.whatsapp_number ?? null,
          })
          setFirmError(null)
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setFirm(null)
          setFirmError(e?.message === 'not_found' ? 'Firm not found' : 'Could not load firm information.')
        }
      })
      .finally(() => {
        if (!cancelled) setFirmLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [firmSlug])

  async function submit() {
    if (!firmSlug) return
    setBusy(true)
    setErr(null)
    try {
      await axios.post(`${API}/api/portal/${firmSlug}/self-register`, {
        client_name,
        business_name: business_name || null,
        email,
        phone,
        country,
        entity_type,
        services,
        financial_year_end: financial_year_end || null,
      })
      setDone(true)
    } catch (e: any) {
      setErr(e?.response?.data?.detail || e?.message || 'Something went wrong')
    } finally {
      setBusy(false)
    }
  }

  if (!firmSlug) {
    return <div className="min-h-screen noise p-8 text-slate-400">Invalid link</div>
  }

  const accent = firm?.primary_color || '#2563EB'
  const initial = (firm?.firm_name || 'F').trim().charAt(0).toUpperCase()

  return (
    <div className="min-h-screen noise flex flex-col">
      {firmLoading ? (
        <div className="bg-gray-900 px-6 py-4 border-b border-gray-800 animate-pulse">
          <div className="h-6 w-48 bg-gray-700 rounded" />
          <div className="h-3 w-32 bg-gray-800 rounded mt-2" />
        </div>
      ) : firmError ? (
        <header className="bg-gray-900 px-6 py-4 border-b border-red-900/50">
          <div className="font-bold text-white text-base">CPAOS</div>
          <div className="text-sm text-red-400 mt-1">{firmError}</div>
        </header>
      ) : firm ? (
        <header
          style={{ borderBottom: `3px solid ${accent}` }}
          className="bg-gray-900 px-6 py-4 flex items-center gap-3"
        >
          {firm.logo_url && !logoFailed ? (
            <img
              src={firm.logo_url}
              alt={firm.firm_name}
              className="h-10 w-auto max-w-[160px] object-contain rounded-lg"
              onError={() => setLogoFailed(true)}
            />
          ) : (
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-lg shrink-0"
              style={{ background: accent }}
            >
              {initial}
            </div>
          )}
          <div>
            <div className="font-bold text-white text-base">{firm.firm_name}</div>
            <div className="text-xs text-gray-400">Client Document Portal</div>
          </div>
        </header>
      ) : (
        <header className="bg-gray-900 px-6 py-4 border-b border-gray-800">
          <div className="font-bold text-white text-base">CPAOS</div>
          <div className="text-xs text-gray-400">Client Document Portal</div>
        </header>
      )}

      <main className="flex-1 px-4 py-8 max-w-xl mx-auto w-full">
        <div className="rounded-2xl border border-border bg-card p-8">
          {done ? (
            <p className="text-sm text-slate-200">
              Check your WhatsApp — we&apos;ve sent your document portal link!
            </p>
          ) : firmError === 'Firm not found' ? null : (
            <>
              <div className="mt-2 space-y-3">
                <input
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                  placeholder="Full name *"
                  value={client_name}
                  onChange={(e) => setClientName(e.target.value)}
                />
                <input
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                  placeholder="Business name"
                  value={business_name}
                  onChange={(e) => setBusinessName(e.target.value)}
                />
                <input
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                  placeholder="Email *"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <input
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                  placeholder="WhatsApp number *"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>

              <div className="mt-8 space-y-4">
                <div>
                  <div className="text-xs text-slate-400 mb-1">Country</div>
                  <select
                    className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                    value={country}
                    onChange={(e) => {
                      setCountry(e.target.value)
                      const next = entityOptions[e.target.value]?.[0] || 'other'
                      setEntityType(next)
                    }}
                  >
                    {countries.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))}
                  </select>
                  <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                    <CountryFlag country={country} />
                    Checklist templates follow this country
                  </div>
                </div>
                <div>
                  <div className="text-xs text-slate-400 mb-1">Entity type</div>
                  <select
                    className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                    value={entity_type}
                    onChange={(e) => setEntityType(e.target.value)}
                  >
                    {entities.map((x) => (
                      <option key={x} value={x}>
                        {x}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <div className="text-xs text-slate-400 mb-2">Services needed</div>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    {['bookkeeping', 'tax', 'gst', 'vat', 'audit'].map((s) => (
                      <label key={s} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={services.includes(s)}
                          onChange={() =>
                            setServices((prev) => (prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]))
                          }
                        />
                        {s}
                      </label>
                    ))}
                  </div>
                </div>
                <input
                  className="w-full rounded-lg border border-border bg-bg px-3 py-2 text-sm"
                  placeholder="Financial year end (optional)"
                  value={financial_year_end}
                  onChange={(e) => setFye(e.target.value)}
                />
              </div>

              {err ? <p className="text-sm text-red-400 mt-4">{err}</p> : null}

              <button
                type="button"
                disabled={busy || !client_name || !email || !phone || !!firmError}
                className="mt-6 w-full rounded-lg py-2.5 text-sm font-semibold text-white disabled:opacity-50"
                style={{ backgroundColor: accent }}
                onClick={submit}
              >
                {busy ? 'Submitting…' : 'Submit & start onboarding'}
              </button>
            </>
          )}

          <Link className="text-xs text-slate-500 block mt-6" to="/home">
            ← Back to marketing site
          </Link>
        </div>
      </main>

      {firm?.whatsapp_number ? (
        <div className="text-center py-4 text-xs text-gray-500">
          Questions? WhatsApp us:{' '}
          <a
            href={`https://wa.me/${firm.whatsapp_number.replace(/\D/g, '')}`}
            className="text-green-400 hover:underline"
            target="_blank"
            rel="noreferrer"
          >
            {firm.whatsapp_number}
          </a>
        </div>
      ) : null}
    </div>
  )
}
