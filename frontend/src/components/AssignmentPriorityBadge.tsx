import type { AssignmentPriority } from '../types/assignment'

const PRIORITY_STYLES: Record<AssignmentPriority, { label: string; className: string }> = {
  low: { label: 'Low', className: 'bg-slate-500/10 text-slate-400' },
  medium: { label: 'Medium', className: 'bg-blue-500/10 text-blue-300' },
  high: { label: 'High', className: 'bg-amber-500/10 text-amber-300' },
  urgent: { label: 'Urgent', className: 'bg-red-500/10 text-red-300' },
}

interface AssignmentPriorityBadgeProps {
  priority: AssignmentPriority
}

export function AssignmentPriorityBadge({ priority }: AssignmentPriorityBadgeProps) {
  const style = PRIORITY_STYLES[priority] || PRIORITY_STYLES.medium
  
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium ${style.className}`}>
      {style.label}
    </span>
  )
}
