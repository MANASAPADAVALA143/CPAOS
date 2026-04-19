import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import api from '../lib/api'
import { CountryFlag } from '../components/CountryFlag'

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

export default function NewClient() {
  const nav = useNavigate()
  const [step, setStep] = useState(1)
  const [client_name, setClientName] = useState('')
  const [business_name, setBusinessName] = useState('')
  const [email, setEmail] = useState('')
  const [phone, setPhone] = useState('')
  const [country, setCountry] = useState('India')
  const [entity_type, setEntityType] = useState('private_limited')
  const [services, setServices] = useState<string[]>(['bookkeeping', 'tax'])
  const [send_engagement_letter, setSendEngagement] = useState(false)

  async function submit() {
    try {
      const res = await api.post('/api/clients', {
        client_name,
        business_name: business_name || null,
        email,
        phone,
        country,
        entity_type,
        services,
        send_engagement_letter,
      })
      toast.success('Client created')
      nav(`/clients/${res.data.id}`)
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to create client')
    }
  }

  return (
    <div className="min-h-screen noise px-6 py-8 max-w-3xl mx-auto">
      <Link to="/dashboard" className="text-sm text-primary">
        ← Dashboard
      </Link>
      <h1 className="font-display text-2xl font-semibold mt-4">New client</h1>
      <div className="text-xs text-slate-500 mt-1">Step {step} of 3</div>

      {step === 1 && (
        <div className="mt-6 space-y-3">
          <input className="w-full rounded-lg border border-border bg-card px-3 py-2" value={client_name} onChange={(e) => setClientName(e.target.value)} placeholder="Client name *" />
          <input className="w-full rounded-lg border border-border bg-card px-3 py-2" value={business_name} onChange={(e) => setBusinessName(e.target.value)} placeholder="Business name" />
          <input className="w-full rounded-lg border border-border bg-card px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email *" type="email" />
          <input className="w-full rounded-lg border border-border bg-card px-3 py-2" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Phone *" />
          <button className="rounded-lg bg-primary px-4 py-2 text-white" type="button" onClick={() => setStep(2)} disabled={!client_name || !email || !phone}>
            Next
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="mt-6 space-y-4">
          <div>
            <div className="text-sm text-slate-400 mb-2">Country</div>
            <select className="w-full rounded-lg border border-border bg-card px-3 py-2" value={country} onChange={(e) => { setCountry(e.target.value); setEntityType(entityOptions[e.target.value][0]) }}>
              {countries.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <div className="text-xs text-slate-500 mt-1 flex items-center gap-1">
              <CountryFlag country={country} />
              Used for checklist templates
            </div>
          </div>
          <div>
            <div className="text-sm text-slate-400 mb-2">Entity type</div>
            <select className="w-full rounded-lg border border-border bg-card px-3 py-2" value={entity_type} onChange={(e) => setEntityType(e.target.value)}>
              {(entityOptions[country] || entityOptions.Other).map((x) => (
                <option key={x} value={x}>
                  {x}
                </option>
              ))}
            </select>
          </div>
          <div>
            <div className="text-sm text-slate-400 mb-2">Services</div>
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
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={send_engagement_letter} onChange={(e) => setSendEngagement(e.target.checked)} />
            Send engagement letter (DocuSign)
          </label>
          <div className="flex gap-2">
            <button className="rounded-lg border border-border px-4 py-2" type="button" onClick={() => setStep(1)}>
              Back
            </button>
            <button className="rounded-lg bg-primary px-4 py-2 text-white" type="button" onClick={() => setStep(3)}>
              Next
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="mt-6 space-y-4">
          <div className="rounded-xl border border-border bg-card p-4 text-sm text-slate-300">
            Review: {client_name} · {country} · {entity_type} · services: {services.join(', ')}
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg border border-border px-4 py-2" type="button" onClick={() => setStep(2)}>
              Back
            </button>
            <button className="rounded-lg bg-primary px-4 py-2 text-white" type="button" onClick={submit}>
              Create client & send portal
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
