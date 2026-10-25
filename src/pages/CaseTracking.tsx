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
  Paperclip,
  Search,
  Send,
  Shield,
  UserCheck,
} from 'lucide-react'
import type { Complaint, Role, Status, UserProfile } from '../types'
import {
  canAddCaseRemarks,
  canUpdateCaseStatus,
  fmt,
  getDaysRemaining,
  getInstitution,
  instName,
  isOverdue,
} from '../data'
import { Badge, Button, Card, CardHeader, PageTitle, SearchBox } from '../components/ui'

interface CaseTrackingProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus: (id: string, s: Status, note?: string) => void
  onAddNote?: (id: string, noteText: string) => void
  currentRole?: Role
  currentUser?: UserProfile
}

export default function CaseTracking({
  complaints,
  onOpen,
  onStatus,
  onAddNote,
  currentRole = 'Admin',
  currentUser,
}: CaseTrackingProps) {
  const [selectedCaseId, setSelectedCaseId] = useState(complaints[0]?.id || '')
  const [searchQuery, setSearchQuery] = useState('')
  const [followUpNote, setFollowUpNote] = useState('')

  // Scoped complaints list based on role
  const roleScopedComplaints = complaints.filter((c) => {
    if (currentRole === 'Complainant') {
      return Boolean(
        currentUser?.email &&
        c.complainantEmail &&
        c.complainantEmail.trim().toLowerCase() === currentUser.email.trim().toLowerCase()
      )
    }
    if (currentRole === 'Officer') {
      return (
        c.officer === currentUser?.name ||
        Boolean(currentUser?.id && c.assignedUserId === currentUser.id)
      )
    }
    if (currentRole === 'BureauAdmin') {
      return currentUser?.bureau === 'All' || c.bureau.toUpperCase() === currentUser?.bureau.toUpperCase()
    }
    return true
  })

  const activeComplaint =
    roleScopedComplaints.find((c) => c.id === selectedCaseId) ||
    roleScopedComplaints[0] ||
    null

  const inst = getInstitution(activeComplaint?.institutionId)
  const overdue = activeComplaint ? isOverdue(activeComplaint) : false
  const daysLeft = activeComplaint ? getDaysRemaining(activeComplaint.due) : 0

  // Permission check for remarks
  const remarkCheck = activeComplaint
    ? canAddCaseRemarks(currentUser, activeComplaint)
    : { allowed: false, reason: 'No active complaint.' }

  // 5 Statutory Milestones for AICTE Complaint Redressal
  const milestones = [
    {
      title: 'Portal Filing & Triage',
      desc: 'Complaint logged, verified, and categorised by automated intake',
      done: true,
      current: false,
    },
    {
      title: 'Bureau Jurisdiction',
      desc: `Jurisdiction established with ${activeComplaint?.bureau} Cell`,
      done: true,
      current: activeComplaint?.status === 'Pending',
    },
    {
      title: 'Preliminary Inquiry',
      desc:
        currentRole === 'Complainant'
          ? 'Under verification with institute registrar'
          : `Assigned to ${activeComplaint?.officer} for record audit`,
      done: activeComplaint?.status !== 'Pending',
      current: activeComplaint?.status === 'In Progress',
    },
    {
      title: 'Hearing & Notice',
      desc: 'Notice served to management; compliance documents requested',
      done: activeComplaint?.status === 'Resolved' || activeComplaint?.status === 'Escalated',
      current: activeComplaint?.status === 'Escalated',
    },
    {
      title: 'Determination & Order',
      desc: 'Compliance accepted or statutory regulatory penalty issued',
      done: activeComplaint?.status === 'Resolved',
      current: false,
    },
  ]

  const filteredList = roleScopedComplaints.filter(
    (c) =>
      !searchQuery.trim() ||
      c.id.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
      c.title.toLowerCase().includes(searchQuery.toLowerCase().trim()) ||
      (c.institutionPermanentId &&
        c.institutionPermanentId.toLowerCase().includes(searchQuery.toLowerCase().trim())) ||
      instName(c.institutionId).toLowerCase().includes(searchQuery.toLowerCase().trim())
  )

  const handleFollowUpSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!followUpNote.trim() || !onAddNote || !activeComplaint || !remarkCheck.allowed) return
    onAddNote(activeComplaint.id, followUpNote.trim())
    setFollowUpNote('')
  }

  // Filter documents visible to current role
  const visibleDocs = (activeComplaint?.documents || []).filter((doc) => {
    if (currentRole === 'Complainant') {
      return doc.visibility === 'Public'
    }
    return true
  })

  if (!activeComplaint) {
    return (
      <div className="space-y-6">
        <PageTitle
          title="Live Case Tracking &amp; SLA Surveillance"
          sub="No complaints currently available for this view"
        />
        <Card className="py-16 text-center text-xs text-slate-500">
          No active case files to display.
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageTitle
        title={
          currentRole === 'Complainant'
            ? 'Track My Grievance Lifecycle'
            : 'Live Case Tracking &amp; SLA Surveillance'
        }
        sub="Monitor lifecycle progression, inquiry milestones, and statutory resolution compliance for any case file"
        tag={currentRole === 'Complainant' ? 'Citizen SLA Tracker' : 'SLA Monitor'}
      />

      {/* Case Selector and Search */}
      <Card padding="p-4">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              {currentRole === 'Complainant'
                ? 'Select One of Your Dockets to Track:'
                : 'Select or Search Complaint Case:'}
            </span>
            <div className="w-72">
              <SearchBox
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search case ID, Permanent PID, or institute..."
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
        {/* Left Column: Lifecycle Progress Steps, Documents & Audit Log */}
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
                <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                  <span>
                    Target: <strong>{instName(activeComplaint.institutionId)}</strong>
                  </span>
                  <span>•</span>
                  <span className="font-mono">
                    PID: <strong>{activeComplaint.institutionPermanentId || inst?.aicteId}</strong>
                  </span>
                  <span>•</span>
                  <span>Filed on {fmt(activeComplaint.date)}</span>
                </div>

                {/* Scheduled Next Administrative Action */}
                <div className="mt-3 rounded-lg bg-slate-50 p-3 border border-slate-200 text-xs">
                  <div className="font-bold text-slate-700 uppercase text-[10px] tracking-wider">
                    Next Statutory Action Milestone:
                  </div>
                  <div className="text-slate-900 font-semibold mt-0.5">
                    {activeComplaint.nextAction || 'Preliminary scrutiny and registrar representation'}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onOpen(activeComplaint.id)}
                  className="text-xs"
                >
                  <Eye size={13} />
                  <span>Full Case File</span>
                </Button>
              </div>
            </div>

            {/* Visual Milestones Stepper */}
            <div className="mt-8 border-t border-slate-100 pt-6">
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

          {/* Attached Case Documents Snapshot */}
          <Card>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Permitted Documents &amp; Evidence Repository
                </h3>
                <p className="text-xs text-slate-500">
                  {currentRole === 'Complainant'
                    ? 'Official notices and citizen-accessible filings'
                    : 'All filed exhibits, inquiry memos, and counter-affidavits'}
                </p>
              </div>
              <span className="text-xs font-bold text-slate-600 font-mono">
                {visibleDocs.length} Document(s)
              </span>
            </div>

            <div className="space-y-2 mt-4">
              {visibleDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between gap-2 rounded-lg border border-slate-200 bg-slate-50/50 p-2.5 text-xs"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <Paperclip size={14} className="text-teal-600 flex-shrink-0" />
                    <span className="font-semibold text-slate-800 truncate">{doc.name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">({doc.size})</span>
                  </div>
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded font-semibold ${
                      doc.visibility === 'Public'
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                        : 'bg-slate-200 text-slate-700'
                    }`}
                  >
                    {doc.visibility}
                  </span>
                </div>
              ))}

              {visibleDocs.length === 0 && (
                <div className="py-4 text-center text-xs text-slate-400">
                  No public documents currently available for this file.
                </div>
              )}
            </div>
          </Card>

          {/* Full Chronological Progression & Follow-Up Form */}
          <Card>
            <CardHeader
              title="Official Chronological History"
              sub="Timestamped audit trail of all institutional hearings, follow-up filings, and status transitions"
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
                      <p className="text-[11px] text-slate-500 mt-0.5">
                        Authorised by: <span className="font-semibold text-slate-700">{item.by}</span>
                        {item.role && (
                          <span className="ml-1 text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.2 rounded font-mono">
                            {item.role}
                          </span>
                        )}
                      </p>
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

            {/* Follow-up Note Form */}
            <form onSubmit={handleFollowUpSubmit} className="mt-6 border-t border-slate-100 pt-4">
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                {currentRole === 'Complainant'
                  ? 'Submit Additional Information / Follow-Up on this Docket:'
                  : 'Record Official Hearing Note / Inquiry Action:'}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  disabled={!remarkCheck.allowed}
                  value={followUpNote}
                  onChange={(e) => setFollowUpNote(e.target.value)}
                  placeholder={
                    !remarkCheck.allowed
                      ? remarkCheck.reason
                      : currentRole === 'Complainant'
                      ? 'e.g. Received new fee notice from management on 24-Oct; requesting expedited review...'
                      : 'e.g. Scrutiny hearing conducted with institute dean; response awaited by 30-Oct...'
                  }
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:border-navy-600 focus:outline-none disabled:bg-slate-100 disabled:text-slate-400"
                />
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  className="text-xs"
                  disabled={!remarkCheck.allowed}
                >
                  <Send size={13} />
                  <span>Submit</span>
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Right Column: Statutory SLA Metrics & Actions */}
        <div className="space-y-6">
          {/* SLA Performance Card */}
          <Card className="border-t-4 border-t-amber-500">
            <CardHeader
              title="SLA Resolution Status"
              sub="Statutory compliance window surveillance"
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
                  <span className="text-slate-500">Permanent Institution ID:</span>
                  <span className="font-mono font-bold text-slate-800">
                    {activeComplaint.institutionPermanentId || inst?.aicteId}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Bureau Jurisdiction:</span>
                  <span className="font-semibold text-slate-800">
                    {activeComplaint.bureau} Cell
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Responsible Authority:</span>
                  <span className="font-semibold text-slate-800">
                    {currentRole === 'Complainant'
                      ? `${activeComplaint.bureau} Grievance Officer`
                      : activeComplaint.officer}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Last Action Date:</span>
                  <span className="font-semibold text-slate-800">
                    {fmt(activeComplaint.lastActionDate || activeComplaint.date)}
                  </span>
                </div>
              </div>

              {/* Status Update Quick Bar (Only for Officers / Admins) */}
              {currentRole !== 'Complainant' ? (
                <div className="border-t border-slate-100 pt-3">
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-bold text-slate-700">
                      Advance Case Status:
                    </label>
                    <span className="text-[10px] text-slate-500 font-mono">
                      Current: {activeComplaint.status}
                    </span>
                  </div>

                  <div className="space-y-2">
                    {activeComplaint.status === 'Pending' && (
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={() => onStatus(activeComplaint.id, 'In Progress')}
                        disabled={
                          !canUpdateCaseStatus(currentUser, activeComplaint, 'In Progress').allowed
                        }
                        className="w-full text-xs"
                      >
                        Start Preliminary Inquiry (In Progress)
                      </Button>
                    )}

                    {activeComplaint.status === 'In Progress' && (
                      <div className="grid grid-cols-2 gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onStatus(activeComplaint.id, 'Escalated')}
                          disabled={
                            !canUpdateCaseStatus(currentUser, activeComplaint, 'Escalated').allowed
                          }
                          className="text-xs text-rose-700 border-rose-200 hover:bg-rose-50"
                        >
                          Escalate Docket
                        </Button>
                        <Button
                          variant="teal"
                          size="sm"
                          onClick={() => onStatus(activeComplaint.id, 'Resolved')}
                          disabled={
                            !canUpdateCaseStatus(currentUser, activeComplaint, 'Resolved').allowed
                          }
                          className="text-xs"
                        >
                          Mark Resolved
                        </Button>
                      </div>
                    )}

                    {activeComplaint.status === 'Escalated' && (
                      <div className="grid grid-cols-2 gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onStatus(activeComplaint.id, 'In Progress')}
                          disabled={
                            !canUpdateCaseStatus(currentUser, activeComplaint, 'In Progress').allowed
                          }
                          className="text-xs"
                        >
                          Return to Inquiry
                        </Button>
                        <Button
                          variant="teal"
                          size="sm"
                          onClick={() => onStatus(activeComplaint.id, 'Resolved')}
                          disabled={
                            !canUpdateCaseStatus(currentUser, activeComplaint, 'Resolved').allowed
                          }
                          className="text-xs"
                        >
                          Mark Resolved
                        </Button>
                      </div>
                    )}

                    {activeComplaint.status === 'Resolved' && (
                      <div className="rounded bg-slate-100 p-2.5 text-center text-[11px] text-slate-600 font-semibold border border-slate-200">
                        Docket Resolved &amp; Closed (Terminal State)
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="rounded-lg bg-slate-100 p-2.5 text-center text-[11px] text-slate-500">
                  Case status is updated by the assigned AICTE {activeComplaint.bureau} inquiry team following statutory review.
                </div>
              )}
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
