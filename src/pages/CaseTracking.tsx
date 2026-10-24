import { useState } from 'react'
import {
  AlertTriangle,
  ArrowRight,
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  ExternalLink,
  Eye,
  FileCheck2,
  FileSearch,
  FileText,
  GitMerge,
  Search,
  Shield,
  UserCheck,
} from 'lucide-react'
import type { Complaint, Status } from '../types'
import { fmt, getDaysRemaining, getInstitution, instName, isOverdue } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle, SearchBox } from '../components/ui'

interface CaseTrackingProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus: (id: string, s: Status) => void
}

export default function CaseTracking({ complaints, onOpen, onStatus }: CaseTrackingProps) {
  const [selectedCaseId, setSelectedCaseId] = useState(complaints[0].id)
  const [searchQuery, setSearchQuery] = useState('')

  const activeComplaint = complaints.find((c) => c.id === selectedCaseId) || complaints[0]
  const inst = getInstitution(activeComplaint.institutionId)
  const overdue = isOverdue(activeComplaint)
  const daysLeft = getDaysRemaining(activeComplaint.due)

  // 5 Statutory Milestones for AICTE Complaint Redressal
  const milestones = [
    {
      title: 'Portal Filing & Triage',
      desc: 'Complaint logged, verified, and categorised by automated intake',
      done: true,
      current: false,
    },
    {
      title: 'Bureau Allocation',
      desc: `Jurisdiction established with ${activeComplaint.bureau} bureau`,
      done: true,
      current: activeComplaint.status === 'Pending',
    },
    {
      title: 'Preliminary Inquiry',
      desc: `Assigned to ${activeComplaint.officer} for record verification`,
      done: activeComplaint.status !== 'Pending',
      current: activeComplaint.status === 'In Progress',
    },
    {
      title: 'Hearing & Show-Cause',
      desc: 'Notice served to management; compliance documents requested',
      done: activeComplaint.status === 'Resolved' || activeComplaint.status === 'Escalated',
      current: activeComplaint.status === 'Escalated',
    },
    {
      title: 'Final Determination & Order',
      desc: 'Compliance accepted or regulatory penalty issued',
      done: activeComplaint.status === 'Resolved',
      current: false,
    },
  ]

  const filteredList = complaints.filter(
    (c) =>
      !searchQuery.trim() ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
      c.title.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
      instName(c.institutionId).toLowerCase().includes(searchQuery.toLowerCase().trim())
  )

  return (
    <div className="space-y-6">
      <PageTitle
        title="Live Case Tracking &amp; SLA Surveillance"
        sub="Monitor lifecycle progression, inquiry milestones, and statutory resolution compliance for any case file"
        tag="SLA Monitor"
      />

      {/* Case Selector Pills and Search */}
      <Card padding="p-4">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Select or Search Complaint Case:
            </span>
            <div className="w-72">
              <SearchBox
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search case ID or institute..."
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 pt-1 max-h-24 overflow-y-auto scrollbar-thin">
            {filteredList.map((c) => {
              const isSelected = selectedCaseId === c.id
              const isCaseOverdue = isOverdue(c)

              return (
                <button
                  key={c.id}
                  onClick={() => setSelectedCaseId(c.id)}
                  className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs font-medium transition border ${
                    isSelected
                      ? 'bg-navy-800 text-white border-navy-800 shadow-2xs font-semibold'
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  <span className="font-mono">{c.id}</span>
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      c.status === 'Resolved'
                        ? 'bg-emerald-400'
                        : isCaseOverdue
                        ? 'bg-rose-400'
                        : 'bg-blue-400'
                    }`}
                  />
                </button>
              )
            })}
          </div>
        </div>
      </Card>

      {/* Selected Case Tracker Detail */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Lifecycle Progress Steps & Audit Log */}
        <div className="space-y-6 lg:col-span-2">
          {/* Active Case Summary Card */}
          <Card className="border-t-4 border-t-navy-800">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-xl font-bold text-navy-900">
                    {activeComplaint.id}
                  </span>
                  <Badge v={activeComplaint.bureau} />
                  <Badge v={activeComplaint.priority} dot />
                  <Badge v={activeComplaint.status} />
                </div>
                <h2 className="text-base font-bold text-slate-900 leading-snug">
                  {activeComplaint.title}
                </h2>
                <p className="text-xs text-slate-500">
                  Target: <strong>{instName(activeComplaint.institutionId)}</strong> • Filed on{' '}
                  {fmt(activeComplaint.date)}
                </p>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onOpen(activeComplaint.id)}
                  className="text-xs"
                >
                  <Eye size={13} />
                  <span>Full File Dossier</span>
                </Button>
              </div>
            </div>

            {/* Visual Milestones Stepper */}
            <div className="mt-8">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-4">
                Statutory Milestone Progression
              </h3>
              <div className="relative flex flex-col sm:flex-row justify-between gap-4">
                {milestones.map((m, idx) => {
                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center text-center relative group">
                      {/* Circle Indicator */}
                      <div
                        className={`flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold transition shadow-xs ${
                          m.done
                            ? 'bg-emerald-600 text-white'
                            : m.current
                            ? 'bg-navy-800 text-white ring-4 ring-navy-100 animate-pulse'
                            : 'bg-slate-200 text-slate-500'
                        }`}
                      >
                        {m.done ? <CheckCircle2 size={18} /> : idx + 1}
                      </div>
                      <h4 className="mt-2 text-xs font-bold text-slate-900">{m.title}</h4>
                      <p className="mt-0.5 text-[10px] text-slate-500 max-w-[140px] leading-tight">
                        {m.desc}
                      </p>
                    </div>
                  )
                })}
              </div>
            </div>
          </Card>

          {/* Full Chronological Progression */}
          <Card>
            <CardHeader
              title="Official Timeline Records"
              sub="Timestamped audit trail of all institutional hearings and status transitions"
            />
            <div className="space-y-4">
              {activeComplaint.timeline.map((item, idx) => (
                <div
                  key={idx}
                  className="flex gap-4 p-3 rounded-lg border border-slate-100 bg-slate-50/60"
                >
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white border border-slate-200 text-navy-800 flex-shrink-0">
                    <Clock size={16} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <h5 className="text-xs font-bold text-slate-900">{item.label}</h5>
                      <span className="text-[11px] font-mono text-slate-400">{fmt(item.date)}</span>
                    </div>
                    {item.by && (
                      <p className="text-[11px] text-slate-500 mt-0.5">Authorised by: {item.by}</p>
                    )}
                    {item.note && (
                      <p className="mt-1 text-xs text-slate-700 bg-white p-2 rounded border border-slate-100">
                        {item.note}
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column: Statutory SLA Metrics & Actions */}
        <div className="space-y-6">
          {/* SLA Performance Card */}
          <Card className="border-t-4 border-t-amber-500">
            <CardHeader
              title="Statutory SLA Status"
              sub="Rule 14 of AICTE Grievance Redressal Regulations"
            />

            <div className="space-y-4">
              <div
                className={`rounded-xl p-4 text-center border ${
                  activeComplaint.status === 'Resolved'
                    ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                    : overdue
                    ? 'bg-rose-50 border-rose-200 text-rose-900'
                    : 'bg-amber-50 border-amber-200 text-amber-900'
                }`}
              >
                <div className="text-xs font-semibold uppercase tracking-wider">
                  Resolution Deadline Status
                </div>
                <div className="text-2xl font-bold mt-1">
                  {activeComplaint.status === 'Resolved'
                    ? 'Resolved & Closed'
                    : overdue
                    ? `${Math.abs(daysLeft)} Days Overdue`
                    : `${daysLeft} Days Remaining`}
                </div>
                <div className="text-xs mt-1 opacity-80">
                  Target Due Date: {fmt(activeComplaint.due)}
                </div>
              </div>

              <div className="space-y-2 rounded-lg bg-slate-50 p-3 text-xs border border-slate-100">
                <div className="flex justify-between">
                  <span className="text-slate-500">Registration Date:</span>
                  <span className="font-semibold text-slate-800">{fmt(activeComplaint.date)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Statutory SLA Window:</span>
                  <span className="font-semibold text-slate-800">14 Business Days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Bureau Jurisdiction:</span>
                  <span className="font-semibold text-slate-800">{activeComplaint.bureau}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Current Officer:</span>
                  <span className="font-semibold text-slate-800">{activeComplaint.officer}</span>
                </div>
              </div>

              {/* Status Update Quick Bar */}
              <div className="border-t border-slate-100 pt-3">
                <label className="block text-xs font-bold text-slate-700 mb-2">
                  Advance Case Status:
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onStatus(activeComplaint.id, 'In Progress')}
                    disabled={activeComplaint.status === 'In Progress'}
                    className="text-xs"
                  >
                    Set In Progress
                  </Button>
                  <Button
                    variant="teal"
                    size="sm"
                    onClick={() => onStatus(activeComplaint.id, 'Resolved')}
                    disabled={activeComplaint.status === 'Resolved'}
                    className="text-xs"
                  >
                    Mark Resolved
                  </Button>
                </div>
              </div>
            </div>
          </Card>

          {/* Quick Institute Summary */}
          <Card>
            <CardHeader title="Institution Profile" />
            <div className="space-y-2 text-xs">
              <div className="font-bold text-slate-900">{inst?.name}</div>
              <div className="text-slate-500">
                {inst?.city}, {inst?.state}
              </div>
              <div className="text-[11px] text-slate-400">
                Permanent AICTE ID: <strong>{inst?.aicteId}</strong>
              </div>
              <div className="pt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onOpen(activeComplaint.id)}
                  className="w-full text-xs"
                >
                  <span>Open Full Case File</span>
                  <ArrowRight size={13} />
                </Button>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
