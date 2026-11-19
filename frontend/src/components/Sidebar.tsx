import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  CheckSquare,
  FileText,
  Calendar,
  DollarSign,
  Clock,
  FileCheck,
  Calculator,
  Settings,
  LogOut,
} from 'lucide-react'
import { supabase } from '../lib/supabase'
import { useFirm } from '../hooks/useFirm'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Clients', href: '/clients', icon: Users },
  { name: 'Assignments', href: '/assignments', icon: ClipboardList },
  { name: 'My Tasks', href: '/my-tasks', icon: CheckSquare },
  { name: 'Review Queue', href: '/review-queue', icon: FileText },
  { name: 'Compliance', href: '/compliance/dashboard', icon: Calendar },
  { name: 'Billing', href: '/billing', icon: DollarSign },
  { name: 'Audit', href: '/audit/dashboard', icon: FileCheck },
  { name: 'Accounting', href: '/accounting/dashboard', icon: Calculator },
  { name: 'Timesheets', href: '/timesheets', icon: Clock, badge: 'Coming Soon' },
]

const bottomNavigation = [
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const { data: firmCtx } = useFirm()

  async function handleLogout() {
    await supabase.auth.signOut()
    window.location.href = '/login'
  }

  return (
    <div className="flex h-screen w-64 flex-col border-r border-border bg-[#0B1D33]">
      {/* Logo & Firm Name */}
      <div className="border-b border-border p-6">
        <h1 className="text-xl font-bold text-white">GNANOVA</h1>
        <p className="text-xs text-[#C9A227] mt-0.5">CA PRACTICE OS</p>
        {firmCtx && (
          <p className="text-xs text-slate-400 mt-2 truncate">{firmCtx.firm.name}</p>
        )}
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href || location.pathname.startsWith(item.href + '/')
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                  ${
                    isActive
                      ? 'bg-[#C9A227]/15 text-[#C9A227]'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }
                  ${item.badge ? 'cursor-not-allowed opacity-50' : ''}
                `}
                onClick={(e) => {
                  if (item.badge) e.preventDefault()
                }}
              >
                <Icon className="h-5 w-5" />
                <span className="flex-1">{item.name}</span>
                {item.badge && (
                  <span className="rounded-full bg-slate-700 px-2 py-0.5 text-[10px] text-slate-300">
                    {item.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Bottom Navigation */}
      <div className="border-t border-border p-4">
        <div className="space-y-1">
          {bottomNavigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`
                  flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                  ${
                    isActive
                      ? 'bg-[#C9A227]/15 text-[#C9A227]'
                      : 'text-slate-300 hover:bg-white/5 hover:text-white'
                  }
                `}
              >
                <Icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            )
          })}
          
          {firmCtx && (
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-300 transition-colors hover:bg-white/5 hover:text-white"
            >
              <LogOut className="h-5 w-5" />
              <span>Log out</span>
            </button>
          )}
        </div>
        
        {firmCtx && (
          <div className="mt-4 rounded-lg bg-white/5 p-3">
            <p className="text-xs font-medium text-slate-300">{firmCtx.user.full_name}</p>
            <p className="text-xs text-slate-500">{firmCtx.user.role}</p>
          </div>
        )}
      </div>
    </div>
  )
}
