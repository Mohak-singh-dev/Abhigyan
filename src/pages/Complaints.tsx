import { useState } from 'react'
import {
  AlertTriangle,
  ArrowLeft,
  Building2,
  Calendar,
  CheckCircle2,
  Clock,
  Download,
  ExternalLink,
  Eye,
  FileCheck,
  FilePlus,
  FileText,
  Filter,
  History,
  Paperclip,
  Plus,
  RotateCcw,
  Send,
  Shield,
  UserCheck,
  UserCog,
} from 'lucide-react'
import type { Bureau, Complaint, Priority, Status } from '../types'
import {
  BUREAUS,
  BUREAU_INFO,
  OFFICERS,
  STATUSES,
  TODAY,
  fmt,
  getDaysRemaining,
  getInstitution,
  instName,
  institutions,
  isOverdue,
} from '../data'
import { Badge, Button, Card, CardHeader, Modal, PageTitle, SearchBox } from '../components/ui'
import ComplaintTable from '../components/ComplaintTable'

interface ComplaintsPageProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus: (id: string, s: Status) => void
  onAddComplaint?: (newComplaint: Complaint) => void
  onNavigateToInstitution?: (instId: string) => void
}

export function ComplaintsPage({
  complaints,
  onOpen,
  onStatus,
  onAddComplaint,
}: ComplaintsPageProps) {
  const [q, setQ] = useState('')
  const [bureau, setBureau] = useState('All')
  const [status, setStatus] = useState('All')
  const [priority, setPriority] = useState('All')
  const [complainant, setComplainant] = useState('All')
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)

  // New complaint form state
  const [newTitle, setNewTitle] = useState('')
  const [newInstId, setNewInstId] = useState(institutions[0].id)
  const [newBureau, setNewBureau] = useState<Bureau>('PGRC')
  const [newCategory, setNewCategory] = useState('Fee Regulation')
  const [newPriority, setNewPriority] = useState<Priority>('High')
  const [newComplainant, setNewComplainant] = useState<'Student' | 'Faculty' | 'Parent' | 'Whistleblower'>('Student')
  const [newDesc, setNewDesc] = useState('')

  const filtered = complaints.filter((c) => {
    const inst = institutions.find((i) => i.id === c.institutionId)
    const text = `${c.id} ${c.title} ${c.category} ${c.officer} ${inst?.name || ''} ${inst?.city || ''}`.toLowerCase()
    const matchesSearch = !q.trim() || text.includes(q.toLowerCase().trim())
    const matchesBureau = bureau === 'All' || c.bureau === bureau
    const matchesStatus = status === 'All' || c.status === status
    const matchesPriority = priority === 'All' || c.priority === priority
    const matchesComplainant = complainant === 'All' || c.complainantType === complainant
    return matchesSearch && matchesBureau && matchesStatus && matchesPriority && matchesComplainant
  })

  const resetFilters = () => {
    setQ('')
    setBureau('All')
    setStatus('All')
    setPriority('All')
    setComplainant('All')
  }

  const handleCreateComplaint = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTitle.trim() || !newDesc.trim()) return

    const prefix = newBureau === 'Approval' ? 'AB' : newBureau === 'Academic' ? 'ACD' : newBureau
    const newId = `${prefix}-2026-${String(Math.floor(Math.random() * 900) + 100)}`
    const defaultOfficer = OFFICERS[0]
    const dueDate = new Date()
    dueDate.setDate(dueDate.getDate() + 14)
    const dueStr = dueDate.toISOString().slice(0, 10)

    const created: Complaint = {
      id: newId,
      institutionId: newInstId,
      bureau: newBureau,
      category: newCategory,
      priority: newPriority,
      officer: defaultOfficer,
      status: 'Pending',
      date: TODAY,
      due: dueStr,
      title: newTitle,
      description: newDesc,
      complainantType: newComplainant,
      attachmentsCount: 1,
      timeline: [
        { label: 'Grievance submitted via AICTE portal', date: TODAY, by: `${newComplainant}` },
        { label: `Assigned to ${defaultOfficer} (${newBureau} Bureau)`, date: TODAY, by: 'Central Dispatch' },
      ],
      assignments: [{ officer: defaultOfficer, date: TODAY, by: 'Admin (Dr. S. Mehta)' }],
    }

    if (onAddComplaint) {
      onAddComplaint(created)
    }

    // Reset & close
    setNewTitle('')
    setNewDesc('')
    setIsAddModalOpen(false)
  }

  const exportCSV = () => {
    const headers = ['Case ID', 'Institution', 'Bureau', 'Category', 'Priority', 'Officer', 'Status', 'Date', 'Due Date']
    const rows = filtered.map((c) => [
      c.id,
      `"${instName(c.institutionId)}"`,
      c.bureau,
      `"${c.category}"`,
      c.priority,
      `"${c.officer}"`,
      c.status,
      c.date,
      c.due,
    ])
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `AICTE_CaseTrack_Complaints_${TODAY}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const isFiltered = q || bureau !== 'All' || status !== 'All' || priority !== 'All' || complainant !== 'All'

  return (
    <div className="space-y-5">
      <PageTitle
        title="All Complaints Directory"
        sub={`Active registry of ${complaints.length} institution complaints across AICTE bureaus`}
        action={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={exportCSV} className="text-xs">
              <Download size={14} />
              <span>Export CSV</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => setIsAddModalOpen(true)}
              className="text-xs"
            >
              <Plus size={14} />
              <span>Register Complaint</span>
            </Button>
          </div>
        }
      />

      {/* Filter and Search Bar */}
      <Card padding="p-4">
        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <SearchBox
              value={q}
              onChange={setQ}
              placeholder="Search by Case ID, institute, city, subject, or officer..."
              className="flex-1 min-w-[260px]"
            />

            {/* Bureau Filter */}
            <select
              value={bureau}
              onChange={(e) => setBureau(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              aria-label="Bureau filter"
            >
              <option value="All">All Bureaus</option>
              {BUREAUS.map((b) => (
                <option key={b} value={b}>
                  Bureau: {b}
                </option>
              ))}
            </select>

            {/* Status Filter */}
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              aria-label="Status filter"
            >
              <option value="All">All Statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  Status: {s}
                </option>
              ))}
            </select>

            {/* Priority Filter */}
            <select
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              aria-label="Priority filter"
            >
              <option value="All">All Priorities</option>
              {['Critical', 'High', 'Medium', 'Low'].map((p) => (
                <option key={p} value={p}>
                  Priority: {p}
                </option>
              ))}
            </select>

            {/* Complainant Filter */}
            <select
              value={complainant}
              onChange={(e) => setComplainant(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              aria-label="Complainant filter"
            >
              <option value="All">All Complainants</option>
              {['Student', 'Faculty', 'Parent', 'Whistleblower'].map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {isFiltered && (
              <Button
                variant="ghost"
                size="sm"
                onClick={resetFilters}
                className="text-xs text-rose-600 hover:text-rose-800"
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </Button>
            )}
          </div>

          <div className="flex items-center justify-between text-xs text-slate-500 border-t border-slate-100 pt-2">
            <div>
              Showing <strong className="text-slate-800">{filtered.length}</strong> of{' '}
              {complaints.length} complaints
            </div>
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-red-500" />
                <span>Critical: {complaints.filter((c) => c.priority === 'Critical').length}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-amber-500" />
                <span>Pending: {complaints.filter((c) => c.status === 'Pending').length}</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="h-2 w-2 rounded-full bg-emerald-500" />
                <span>Resolved: {complaints.filter((c) => c.status === 'Resolved').length}</span>
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Main Table */}
      <ComplaintTable
        rows={filtered}
        onOpen={onOpen}
        onStatus={onStatus}
        compact={false}
        showActions={true}
      />

      {/* Register Complaint Modal */}
      <Modal
        open={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        title="Register New Institution Complaint"
        subtitle="Log a formal grievance or regulatory non-compliance file into AICTE CaseTrack"
      >
        <form onSubmit={handleCreateComplaint} className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Target Institution *
              </label>
              <select
                value={newInstId}
                onChange={(e) => setNewInstId(e.target.value)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                {institutions.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.name} ({i.city})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Jurisdiction Bureau *
              </label>
              <select
                value={newBureau}
                onChange={(e) => setNewBureau(e.target.value as Bureau)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                {BUREAUS.map((b) => (
                  <option key={b} value={b}>
                    {BUREAU_INFO[b]?.name || b}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Category *
              </label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                <option value="Fee Regulation">Fee Regulation</option>
                <option value="Faculty Norms">Faculty Norms</option>
                <option value="Infrastructure">Infrastructure</option>
                <option value="Admission Irregularity">Admission Irregularity</option>
                <option value="Unapproved Courses">Unapproved Courses</option>
                <option value="Harassment & Ragging">Harassment &amp; Ragging</option>
                <option value="Certificate Delay">Certificate Delay</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Priority Severity *
              </label>
              <select
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value as Priority)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                <option value="Critical">Critical (Immediate hearing)</option>
                <option value="High">High (7-day SLA)</option>
                <option value="Medium">Medium (14-day SLA)</option>
                <option value="Low">Low (30-day SLA)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Complainant Type *
              </label>
              <select
                value={newComplainant}
                onChange={(e) => setNewComplainant(e.target.value as any)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                <option value="Student">Enrolled Student</option>
                <option value="Parent">Parent / Guardian</option>
                <option value="Faculty">Faculty Member</option>
                <option value="Whistleblower">Anonymous Whistleblower</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Case Subject / Title *
            </label>
            <input
              type="text"
              required
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="e.g. Unauthorised collection of examination fees beyond approved ceiling"
              className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-navy-600 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Detailed Complaint Narrative &amp; Facts *
            </label>
            <textarea
              required
              rows={4}
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="Provide complete details including batch, department, notice circular dates, or specific violations..."
              className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 placeholder-slate-400 focus:border-navy-600 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 border-t border-slate-100 pt-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setIsAddModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="sm">
              <FilePlus size={14} />
              <span>Submit Case File</span>
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}

export function DetailsPage({
  complaint: c,
  onBack,
  onStatus,
  onAssign,
  onAddNote,
  onNavigateToInstitution,
}: {
  complaint?: Complaint
  onBack: () => void
  onStatus: (id: string, s: Status) => void
  onAssign: (id: string, o: string) => void
  onAddNote?: (id: string, noteText: string) => void
  onNavigateToInstitution?: (instId: string) => void
}) {
  const [newRemark, setNewRemark] = useState('')
  const [selectedOfficer, setSelectedOfficer] = useState(c?.officer || OFFICERS[0])

  if (!c) {
    return (
      <div className="space-y-4">
        <Button variant="outline" size="sm" onClick={onBack}>
          <ArrowLeft size={16} /> Back to complaints
        </Button>
        <Card className="py-12 text-center text-sm text-slate-500">
          Complaint not found or has been removed.
        </Card>
      </div>
    )
  }

  const inst = getInstitution(c.institutionId)
  const overdue = isOverdue(c)
  const daysRemaining = getDaysRemaining(c.due)

  const handleAddRemark = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newRemark.trim() || !onAddNote) return
    onAddNote(c.id, newRemark.trim())
    setNewRemark('')
  }

  const handleOfficerChange = (officer: string) => {
    setSelectedOfficer(officer)
    onAssign(c.id, officer)
  }

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-3">
        <Button variant="outline" size="sm" onClick={onBack} className="text-xs">
          <ArrowLeft size={14} />
          <span>Back to Complaints</span>
        </Button>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500">Update Status:</span>
          <select
            value={c.status}
            onChange={(e) => onStatus(c.id, e.target.value as Status)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold text-slate-800 shadow-2xs focus:border-navy-600 focus:outline-none"
          >
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Case Header Banner */}
      <Card className="border-l-4 border-l-navy-800 bg-gradient-to-r from-white via-white to-slate-50">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xl font-bold font-mono tracking-tight text-navy-900">
                {c.id}
              </span>
              <Badge v={c.bureau} />
              <Badge v={c.priority} dot />
              <Badge v={c.status} />
              {overdue && (
                <span className="inline-flex items-center gap-1 rounded bg-red-100 px-2 py-0.5 text-xs font-bold text-red-700">
                  <AlertTriangle size={12} /> Overdue ({Math.abs(daysRemaining)} days)
                </span>
              )}
            </div>
            <h2 className="text-lg font-bold text-slate-900 leading-snug">{c.title}</h2>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Calendar size={13} className="text-slate-400" />
                <span>Filed: {fmt(c.date)}</span>
              </span>
              <span className="flex items-center gap-1">
                <Clock size={13} className="text-slate-400" />
                <span>SLA Due: {fmt(c.due)}</span>
              </span>
              <span className="flex items-center gap-1">
                <UserCheck size={13} className="text-slate-400" />
                <span>Complainant: {c.complainantType || 'Student'}</span>
              </span>
            </div>
          </div>

          {/* Quick SLA Badge Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-3 text-right shadow-2xs min-w-[160px]">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              SLA Countdown
            </div>
            <div
              className={`text-xl font-bold mt-0.5 ${
                c.status === 'Resolved'
                  ? 'text-emerald-600'
                  : overdue
                  ? 'text-rose-600'
                  : daysRemaining <= 3
                  ? 'text-amber-600'
                  : 'text-slate-800'
              }`}
            >
              {c.status === 'Resolved'
                ? 'Case Closed'
                : overdue
                ? `${Math.abs(daysRemaining)}d Breached`
                : `${daysRemaining} Days Left`}
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Target Bureau: {c.bureau}
            </div>
          </div>
        </div>
      </Card>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Complaint Narrative & Timeline */}
        <div className="space-y-6 lg:col-span-2">
          {/* Detailed Narrative */}
          <Card>
            <CardHeader
              title="Complaint Substance &amp; Allegations"
              sub="Official grievance statement filed on AICTE CaseTrack"
            />
            <div className="rounded-lg bg-slate-50/80 p-4 border border-slate-200/60 text-slate-800 text-sm leading-relaxed whitespace-pre-line">
              {c.description}
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 border-t border-slate-100 pt-3">
              <div className="flex items-center gap-2">
                <Paperclip size={14} className="text-slate-400" />
                <span>
                  <strong>{c.attachmentsCount || 2}</strong> Supporting Documents Attached (Affidavits, Fee
                  Circulars)
                </span>
              </div>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-600 font-mono text-[11px]">
                Classification: {c.category}
              </span>
            </div>
          </Card>

          {/* Comprehensive Timeline Audit Trail */}
          <Card>
            <CardHeader
              title="Case Audit Trail &amp; Chronology"
              sub="Immutable chronological history of notifications, assignments, and hearings"
            />
            <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              {c.timeline.map((step, idx) => {
                const isLast = idx === c.timeline.length - 1
                return (
                  <div key={idx} className="relative group">
                    <span
                      className={`absolute -left-6 top-1 h-4 w-4 rounded-full border-2 border-white shadow-xs ${
                        isLast ? 'bg-navy-700 ring-4 ring-navy-100' : 'bg-slate-400'
                      }`}
                    />
                    <div className="rounded-lg border border-slate-200/80 bg-white p-3.5 shadow-2xs">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h4 className="text-xs font-bold text-slate-900">{step.label}</h4>
                        <span className="text-[11px] font-medium text-slate-400 font-mono">
                          {fmt(step.date)}
                        </span>
                      </div>
                      {step.by && (
                        <div className="text-[11px] text-slate-500 mt-1">
                          Action by: <span className="font-semibold text-slate-700">{step.by}</span>
                        </div>
                      )}
                      {step.note && (
                        <p className="mt-1.5 text-xs text-slate-600 bg-slate-50 p-2 rounded border border-slate-100">
                          {step.note}
                        </p>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Add Investigation Note Form */}
            <form onSubmit={handleAddRemark} className="mt-6 border-t border-slate-100 pt-4">
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                Record Official Action / Meeting Milestone:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newRemark}
                  onChange={(e) => setNewRemark(e.target.value)}
                  placeholder="e.g. Scrutiny hearing conducted; institution directed to produce fee register..."
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:border-navy-600 focus:outline-none"
                />
                <Button type="submit" variant="primary" size="sm" className="text-xs">
                  <Send size={13} />
                  <span>Log Entry</span>
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Right Column: Institution Info & Officer Assignment */}
        <div className="space-y-6">
          {/* Institution Roster Card */}
          <Card>
            <CardHeader
              title="Target Institution"
              sub="Accredited technical campus profile"
              action={
                onNavigateToInstitution && (
                  <button
                    onClick={() => onNavigateToInstitution(c.institutionId)}
                    className="text-xs text-navy-700 font-semibold hover:underline flex items-center gap-1"
                  >
                    <span>Profile</span>
                    <ExternalLink size={12} />
                  </button>
                )
              }
            />

            {inst ? (
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-navy-50 text-navy-800 font-bold border border-navy-100">
                    <Building2 size={20} />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 leading-snug">{inst.name}</h4>
                    <p className="text-xs text-slate-500">
                      {inst.city}, {inst.state}
                    </p>
                  </div>
                </div>

                <div className="rounded-lg bg-slate-50 p-3 space-y-1.5 text-xs border border-slate-100">
                  <div className="flex justify-between">
                    <span className="text-slate-500">AICTE Permanent ID:</span>
                    <span className="font-mono font-bold text-slate-800">{inst.aicteId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Campus Type:</span>
                    <span className="font-medium text-slate-800">{inst.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">First Approved:</span>
                    <span className="font-medium text-slate-800">{inst.approved}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Risk Assessment:</span>
                    <Badge v={`Risk: ${inst.riskLevel || 'Moderate'}`} />
                  </div>
                </div>

                <div className="text-xs text-slate-500 pt-1">
                  Contact: <span className="font-medium text-slate-700">{inst.contactEmail}</span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-400">Institution details unavailable</div>
            )}
          </Card>

          {/* Assigned Officer & Case Management */}
          <Card>
            <CardHeader
              title="Assigned Investigating Officer"
              sub="Designated AICTE official responsible for this docket"
            />

            <div className="space-y-4">
              <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50/60 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-navy-800 text-white font-bold text-sm">
                  {c.officer.slice(0, 1)}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">{c.officer}</h4>
                  <div className="text-[11px] text-slate-500">Bureau Assignment: {c.bureau}</div>
                  <div className="text-[10px] text-teal-700 font-semibold">Active Docket</div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reassign Case Officer:
                </label>
                <div className="flex gap-2">
                  <select
                    value={selectedOfficer}
                    onChange={(e) => handleOfficerChange(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                  >
                    {OFFICERS.map((off) => (
                      <option key={off} value={off}>
                        {off}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Assignment log */}
              <div className="border-t border-slate-100 pt-3">
                <span className="text-[11px] font-bold text-slate-600 uppercase tracking-wider block mb-2">
                  Assignment History
                </span>
                <div className="space-y-2">
                  {c.assignments.map((a, idx) => (
                    <div
                      key={idx}
                      className="text-xs flex items-center justify-between text-slate-600 bg-slate-50 px-2.5 py-1.5 rounded"
                    >
                      <span>{a.officer}</span>
                      <span className="text-[10px] text-slate-400">{fmt(a.date)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
