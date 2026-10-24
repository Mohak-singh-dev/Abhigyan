import { useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowUpDown,
  Building2,
  Calendar,
  Clock,
  ExternalLink,
  Eye,
  User,
} from 'lucide-react'
import type { Complaint, Status } from '../types'
import { STATUSES, fmt, getDaysRemaining, instName, isOverdue } from '../data'
import { Badge, Button } from './ui'

interface ComplaintTableProps {
  rows: Complaint[]
  onOpen: (id: string) => void
  onStatus?: (id: string, s: Status) => void
  compact?: boolean
  showActions?: boolean
}

type SortField = 'id' | 'institution' | 'bureau' | 'priority' | 'status' | 'date' | 'due'

export default function ComplaintTable({
  rows,
  onOpen,
  onStatus,
  compact = false,
  showActions = true,
}: ComplaintTableProps) {
  const [sortField, setSortField] = useState<SortField>('date')
  const [sortAsc, setSortAsc] = useState<boolean>(false)

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(true)
    }
  }

  const sortedRows = [...rows].sort((a, b) => {
    let cmp = 0
    switch (sortField) {
      case 'id':
        cmp = a.id.localeCompare(b.id)
        break
      case 'institution':
        cmp = instName(a.institutionId).localeCompare(instName(b.institutionId))
        break
      case 'bureau':
        cmp = a.bureau.localeCompare(b.bureau)
        break
      case 'priority': {
        const pOrder: Record<string, number> = { Critical: 4, High: 3, Medium: 2, Low: 1 }
        cmp = (pOrder[a.priority] || 0) - (pOrder[b.priority] || 0)
        break
      }
      case 'status':
        cmp = a.status.localeCompare(b.status)
        break
      case 'date':
        cmp = a.date.localeCompare(b.date)
        break
      case 'due':
        cmp = a.due.localeCompare(b.due)
        break
    }
    return sortAsc ? cmp : -cmp
  })

  if (!rows.length) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
          <AlertCircle size={24} />
        </div>
        <h4 className="mt-3 text-sm font-semibold text-slate-800">No complaints found</h4>
        <p className="mt-1 text-xs text-slate-500">
          No records match your selected bureau, status, or search query.
        </p>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-slate-200">
      <table className="w-full text-left text-xs sm:text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-[11px] font-bold uppercase tracking-wider text-slate-600 select-none">
          <tr>
            <th
              onClick={() => handleSort('id')}
              className="cursor-pointer px-4 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>Case ID</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            <th
              onClick={() => handleSort('institution')}
              className="cursor-pointer px-4 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>Institution</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            <th
              onClick={() => handleSort('bureau')}
              className="cursor-pointer px-3 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>Bureau</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            {!compact && <th className="px-4 py-3">Category &amp; Subject</th>}
            <th
              onClick={() => handleSort('priority')}
              className="cursor-pointer px-3 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>Priority</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            {!compact && <th className="px-3 py-3">Investigating Officer</th>}
            <th
              onClick={() => handleSort('status')}
              className="cursor-pointer px-3 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>Status</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            <th
              onClick={() => handleSort('due')}
              className="cursor-pointer px-3 py-3 hover:bg-slate-100 transition"
            >
              <div className="flex items-center gap-1.5">
                <span>SLA Due</span>
                <ArrowUpDown size={12} className="text-slate-400" />
              </div>
            </th>
            {showActions && <th className="px-4 py-3 text-right">Action</th>}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {sortedRows.map((c) => {
            const overdue = isOverdue(c)
            const daysLeft = getDaysRemaining(c.due)

            return (
              <tr
                key={c.id}
                onClick={() => onOpen(c.id)}
                className="cursor-pointer transition-colors hover:bg-slate-50/80 group"
              >
                {/* Case ID */}
                <td className="whitespace-nowrap px-4 py-3 font-semibold text-navy-800">
                  <div className="flex items-center gap-2">
                    <span className="group-hover:text-navy-600 transition underline-offset-2 group-hover:underline">
                      {c.id}
                    </span>
                    {overdue && (
                      <span
                        className="inline-flex items-center gap-1 rounded bg-red-100 px-1.5 py-0.2 text-[10px] font-bold text-red-700"
                        title="Resolution has breached the statutory SLA"
                      >
                        <AlertTriangle size={11} /> OVERDUE
                      </span>
                    )}
                  </div>
                  <div className="text-[10px] text-slate-400 font-normal sm:hidden truncate max-w-[120px]">
                    {c.category}
                  </div>
                </td>

                {/* Institution */}
                <td className="px-4 py-3">
                  <div className="font-medium text-slate-900 line-clamp-1 max-w-[200px]">
                    {instName(c.institutionId)}
                  </div>
                  <div className="text-[11px] text-slate-400 flex items-center gap-1">
                    <Building2 size={11} />
                    <span>ID: {c.institutionId}</span>
                  </div>
                </td>

                {/* Bureau */}
                <td className="whitespace-nowrap px-3 py-3">
                  <Badge v={c.bureau} />
                </td>

                {/* Category & Subject */}
                {!compact && (
                  <td className="px-4 py-3 max-w-[240px]">
                    <div className="font-medium text-slate-800 line-clamp-1">{c.title}</div>
                    <div className="text-xs text-slate-500 font-normal truncate mt-0.5">
                      {c.category} • by {c.complainantType || 'Student'}
                    </div>
                  </td>
                )}

                {/* Priority */}
                <td className="whitespace-nowrap px-3 py-3">
                  <Badge v={c.priority} dot />
                </td>

                {/* Officer */}
                {!compact && (
                  <td className="whitespace-nowrap px-3 py-3 text-slate-700">
                    <div className="flex items-center gap-1.5">
                      <div className="flex h-5 w-5 items-center justify-center rounded-full bg-slate-200 text-[10px] font-bold text-slate-700">
                        {c.officer.slice(0, 1)}
                      </div>
                      <span className="text-xs">{c.officer}</span>
                    </div>
                  </td>
                )}

                {/* Status */}
                <td
                  className="whitespace-nowrap px-3 py-3"
                  onClick={(e) => onStatus && e.stopPropagation()}
                >
                  {onStatus ? (
                    <select
                      className="rounded-md border border-slate-300 bg-white px-2 py-1 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
                      value={c.status}
                      onChange={(e) => onStatus(c.id, e.target.value as Status)}
                    >
                      {STATUSES.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <Badge v={c.status} />
                  )}
                </td>

                {/* Due Date & SLA countdown */}
                <td className="whitespace-nowrap px-3 py-3">
                  <div className="text-xs text-slate-700 font-medium">{fmt(c.due)}</div>
                  {c.status !== 'Resolved' ? (
                    <div
                      className={`text-[10px] font-medium ${
                        overdue
                          ? 'text-red-600 font-bold'
                          : daysLeft <= 3
                          ? 'text-amber-600 font-semibold'
                          : 'text-slate-400'
                      }`}
                    >
                      {overdue ? `${Math.abs(daysLeft)}d delay` : `${daysLeft}d left`}
                    </div>
                  ) : (
                    <div className="text-[10px] text-emerald-600 font-medium">Closed</div>
                  )}
                </td>

                {/* Actions */}
                {showActions && (
                  <td className="whitespace-nowrap px-4 py-3 text-right">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onOpen(c.id)
                      }}
                      className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold text-navy-800 hover:bg-navy-50 hover:text-navy-900 transition"
                    >
                      <Eye size={14} />
                      <span>Details</span>
                    </button>
                  </td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
