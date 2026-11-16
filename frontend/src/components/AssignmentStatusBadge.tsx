import type { AssignmentStatus } from '../types/assignment'

const STATUS_STYLES: Record<AssignmentStatus, { label: string; className: string }> = {
  created: { label: 'Created', className: 'bg-slate-500/15 text-slate-400 border-slate-500/40' },
  assigned: { label: 'Assigned', className: 'bg-blue-500/15 text-blue-300 border-blue-500/40' },
  in_progress: { label: 'In Progress', className: 'bg-blue-500/15 text-blue-300 border-blue-500/40' },
  submitted: { label: 'Submitted', className: 'bg-amber-500/15 text-amber-300 border-amber-500/40' },
  manager_review: { label: 'Manager Review', className: 'bg-amber-500/15 text-amber-300 border-amber-500/40' },
  partner_review: { label: 'Partner Review', className: 'bg-purple-500/15 text-purple-300 border-purple-500/40' },
  approved: { label: 'Approved', className: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' },
  completed: { label: 'Completed', className: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/40' },
  on_hold: { label: 'On Hold', className: 'bg-slate-500/15 text-slate-400 border-slate-500/40' },
  cancelled: { label: 'Cancelled', className: 'bg-red-500/15 text-red-300 border-red-500/40' },
}

interface AssignmentStatusBadgeProps {
  status: AssignmentStatus
}

export function AssignmentStatusBadge({ status }: AssignmentStatusBadgeProps) {
  const style = STATUS_STYLES[status] || STATUS_STYLES.created
  
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${style.className}`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {style.label}
    </span>
  )
}
