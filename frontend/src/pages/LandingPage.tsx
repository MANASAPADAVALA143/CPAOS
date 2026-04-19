import { Link } from 'react-router-dom'
import {
  ArrowRight,
  Bot,
  Building2,
  CheckCircle2,
  FileCheck2,
  Globe2,
  MessageSquare,
  Shield,
  Sparkles,
  Zap,
} from 'lucide-react'

const DEMO_PORTAL = '/portal/demo-accounting/22222222-2222-2222-2222-222222222222'

const features = [
  {
    icon: Bot,
    title: 'AI document checks',
    body: 'Uploads are classified and matched to your checklist so staff spend less time sorting files.',
  },
  {
    icon: Globe2,
    title: 'Multi-country playbooks',
    body: 'India, UAE, UK, US, and Singapore templates adapt to entity type and services you offer.',
  },
  {
    icon: MessageSquare,
    title: 'WhatsApp + SMS nudges',
    body: 'Remind clients from the app with optional n8n + Twilio fallback when WhatsApp is unavailable.',
  },
  {
    icon: Shield,
    title: 'Secure file handling',
    body: 'Documents live in private storage with time-limited signed URLs—no public buckets required.',
  },
  {
    icon: FileCheck2,
    title: 'Checklist you can trust',
    body: 'Track pending, uploaded, verified, rejected, and waived items in one place per client.',
  },
  {
    icon: Building2,
    title: 'Built for firms',
    body: 'Multi-tenant from day one: each firm only sees its own clients, team, and branding.',
  },
]

const countries = [
  {
    flag: '🇮🇳',
    name: 'India',
    docs: 'PAN, Aadhaar, GST returns, ITR, bank statements, board resolutions',
  },
  {
    flag: '🇦🇪',
    name: 'UAE',
    docs: 'Trade license, Emirates ID, VAT / CT registration, bank statements',
  },
  {
    flag: '🇬🇧',
    name: 'UK',
    docs: 'UTR, Companies House, CT600, SA302, payroll and VAT where applicable',
  },
  {
    flag: '🇺🇸',
    name: 'United States',
    docs: 'EIN, W-2 / 1099, 1040 / 1120, operating agreements, payroll filings',
  },
  {
    flag: '🇸🇬',
    name: 'Singapore',
    docs: 'ACRA BizFile, IRAS filings, CPF, GST where registered',
  },
]

const steps = [
  { n: '1', title: 'Create the client', body: 'Pick country, entity, and services—we generate the checklist.' },
  { n: '2', title: 'Send the portal', body: 'Clients get a branded link; optional engagement letter flow.' },
  { n: '3', title: 'They upload', body: 'Drag-and-drop with AI-assisted classification and smart matching.' },
  { n: '4', title: 'You review', body: 'Approve, reject, or waive items; activity stays auditable.' },
  { n: '5', title: 'Close faster', body: 'Reminders and completion tracking reduce manual chasing.' },
]

const pricing = [
  {
    name: 'Starter',
    price: '₹2,999',
    period: '/mo',
    blurb: 'Small practices getting started with digital onboarding.',
    items: ['Up to 10 active clients', 'Core checklist engine', 'Portal + email flows', 'Email support'],
    cta: 'Get started',
    featured: false,
  },
  {
    name: 'Pro',
    price: '₹7,999',
    period: '/mo',
    blurb: 'Growing firms that want AI checks and heavier client volume.',
    items: [
      'Up to 50 active clients',
      'AI document classification',
      'WhatsApp / SMS reminders',
      'Team roles & activity log',
    ],
    cta: 'Get started',
    featured: true,
  },
  {
    name: 'Agency',
    price: '₹19,999',
    period: '/mo',
    blurb: 'Networks and multi-branch groups that need scale and priority help.',
    items: ['Unlimited clients (fair use)', 'Priority onboarding', 'Custom integrations roadmap', 'Dedicated channel'],
    cta: 'Talk to us',
    featured: false,
  },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen noise bg-bg text-slate-100">
      <header className="border-b border-border/80 bg-bg/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <Link to="/home" className="font-display text-lg font-semibold tracking-tight">
            CPAOS
          </Link>
          <nav className="flex items-center gap-3 text-sm">
            <a href="#features" className="text-slate-400 hover:text-white hidden sm:inline">
              Features
            </a>
            <a href="#pricing" className="text-slate-400 hover:text-white hidden sm:inline">
              Pricing
            </a>
            <Link
              to="/register"
              className="rounded-lg bg-primary px-4 py-2 font-medium text-white shadow-lg shadow-primary/20"
            >
              Create firm account
            </Link>
          </nav>
        </div>
      </header>

      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/10 via-transparent to-transparent pointer-events-none" />
        <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-16 pb-20 sm:pt-24 sm:pb-28 relative">
          <div className="max-w-3xl">
            <p className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-3 py-1 text-xs text-slate-400 mb-6">
              <Sparkles className="w-3.5 h-3.5 text-primary" />
              AI client onboarding for CA &amp; accounting firms
            </p>
            <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-bold leading-tight">
              Onboard clients in days,{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-sky-400">
                not weeks
              </span>
              .
            </h1>
            <p className="mt-6 text-lg text-slate-400 leading-relaxed">
              One branded portal, smart checklists by country, AI-assisted documents, and reminders—so your team
              stops chasing PDFs and starts reviewing work.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row gap-3 sm:items-center">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3.5 text-base font-semibold text-white shadow-xl shadow-primary/25 hover:bg-blue-600 transition-colors"
              >
                Create firm account
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to={DEMO_PORTAL}
                className="inline-flex items-center justify-center text-sm text-primary hover:underline sm:ml-2"
              >
                View demo portal →
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-16 sm:mt-20">
            {[
              { icon: Zap, stat: '10×', label: 'faster intake vs email threads', k: 'speed' },
              { icon: Globe2, stat: '5', label: 'countries with tailored checklists', k: 'countries' },
              { icon: CheckCircle2, stat: '0', label: 'manual chasing with smart reminders', k: 'chase' },
            ].map((s) => (
              <div
                key={s.k}
                className="rounded-2xl border border-border bg-card/80 p-6 flex gap-4 items-start hover:border-primary/30 transition-colors"
              >
                <div className="rounded-lg bg-primary/15 p-2.5 text-primary">
                  <s.icon className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-display text-3xl font-bold text-white">{s.stat}</div>
                  <div className="text-sm text-slate-400 mt-1 leading-snug">{s.label}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="py-20 border-t border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center">Everything firms need to onboard</h2>
          <p className="mt-3 text-center text-slate-400 max-w-2xl mx-auto">
            From first invite to signed engagement and verified documents—CPAOS keeps clients moving without
            another spreadsheet.
          </p>
          <div className="mt-14 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-2xl border border-border bg-card p-6 hover:border-primary/25 transition-colors"
              >
                <div className="w-10 h-10 rounded-lg bg-primary/15 flex items-center justify-center text-primary mb-4">
                  <f.icon className="w-5 h-5" />
                </div>
                <h3 className="font-display text-lg font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">{f.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-card/30 border-y border-border">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center">Checklists that match how you work</h2>
          <p className="mt-3 text-center text-slate-400 max-w-2xl mx-auto">
            Entity-aware lists across major markets—GST when you offer it, CT where it matters, and no generic
            “upload something” steps.
          </p>
          <div className="mt-14 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {countries.map((c) => (
              <div key={c.name} className="rounded-2xl border border-border bg-bg p-6">
                <div className="text-3xl mb-2">{c.flag}</div>
                <h3 className="font-display text-xl font-semibold">{c.name}</h3>
                <p className="mt-3 text-sm text-slate-400 leading-relaxed">{c.docs}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center">How it works</h2>
          <p className="mt-3 text-center text-slate-400">Five steps from invite to completed file.</p>
          <ol className="mt-14 grid gap-6 md:grid-cols-5">
            {steps.map((st) => (
              <li key={st.n} className="relative rounded-2xl border border-border bg-card p-5 pt-8">
                <span className="absolute -top-3 left-5 font-mono text-xs font-bold text-primary bg-bg border border-primary/40 px-2 py-0.5 rounded-md">
                  Step {st.n}
                </span>
                <h3 className="font-display font-semibold">{st.title}</h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">{st.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="pricing" className="py-20 border-t border-border bg-card/20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <h2 className="font-display text-3xl sm:text-4xl font-bold text-center">Simple pricing</h2>
          <p className="mt-3 text-center text-slate-400">Pick a tier that matches your client volume.</p>
          <div className="mt-14 grid lg:grid-cols-3 gap-6">
            {pricing.map((p) => (
              <div
                key={p.name}
                className={`rounded-2xl border p-8 flex flex-col ${
                  p.featured
                    ? 'border-primary bg-gradient-to-b from-primary/15 to-card shadow-xl shadow-primary/10 scale-[1.02] lg:scale-105'
                    : 'border-border bg-card'
                }`}
              >
                <div className="text-sm font-medium text-primary">{p.featured ? 'Most popular' : '\u00a0'}</div>
                <h3 className="font-display text-2xl font-bold mt-2">{p.name}</h3>
                <p className="mt-2 text-sm text-slate-400 flex-1">{p.blurb}</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="font-display text-4xl font-bold">{p.price}</span>
                  <span className="text-slate-500 text-sm">{p.period}</span>
                </div>
                <ul className="mt-6 space-y-3 text-sm text-slate-300">
                  {p.items.map((item) => (
                    <li key={item} className="flex gap-2">
                      <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
                      {item}
                    </li>
                  ))}
                </ul>
                <Link
                  to="/register"
                  className={`mt-8 block text-center rounded-xl py-3 font-semibold transition-colors ${
                    p.featured
                      ? 'bg-primary text-white hover:bg-blue-600'
                      : 'border border-border bg-bg hover:border-primary/40'
                  }`}
                >
                  {p.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 text-center">
          <h2 className="font-display text-3xl sm:text-4xl font-bold">Ready to modernize client onboarding?</h2>
          <p className="mt-4 text-slate-400">
            Open the dashboard to explore the app, or try the demo portal for the client experience—no account required on
            the portal.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-8 py-3.5 font-semibold text-white hover:bg-blue-600"
            >
              Create firm account
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to={DEMO_PORTAL}
              className="inline-flex items-center justify-center rounded-xl border border-border bg-card px-8 py-3.5 font-medium text-slate-200 hover:border-primary/40"
            >
              View demo portal
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-border py-10 text-center text-sm text-slate-500">
        <div className="max-w-6xl mx-auto px-4">
          <p className="font-display text-slate-400">CPAOS</p>
          <p className="mt-2">AI-powered client onboarding for accounting firms.</p>
          <div className="mt-6 flex justify-center gap-6">
            <Link to="/" className="hover:text-white">
              Dashboard
            </Link>
            <Link to={DEMO_PORTAL} className="hover:text-white">
              Demo portal
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
