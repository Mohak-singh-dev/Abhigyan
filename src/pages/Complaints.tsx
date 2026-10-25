import { useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
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
  Info,
  Lock,
  Paperclip,
  Plus,
  RotateCcw,
  Send,
  Shield,
  ShieldAlert,
  Upload,
  User,
  UserCheck,
  UserCog,
  X,
} from 'lucide-react'
import type { Bureau, CaseDocument, Complaint, Priority, ReassignmentRequest, Role, Status, UserProfile } from '../types'
import {
  BUREAUS,
  BUREAU_INFO,
  BUREAU_OFFICERS,
  OFFICERS,
  PERMITTED_STATUS_TRANSITIONS,
  STATUSES,
  TODAY,
  canAddCaseRemarks,
  canAssignCase,
  canReviewReassignmentRequest,
  canTransferBureau,
  canUpdateCaseStatus,
  canUploadCaseDocument,
  fmt,
  getDaysRemaining,
  getInstitution,
  getOfficersForBureau,
  instName,
  institutions,
  isOverdue,
} from '../data'
import { Badge, Button, Card, CardHeader, Modal, PageTitle, SearchBox } from '../components/ui'
import ComplaintTable from '../components/ComplaintTable'

interface ComplaintsPageProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus: (id: string, s: Status, note?: string) => void
  onAddComplaint?: (newComplaint: Complaint) => void
  onNavigateToInstitution?: (instId: string) => void
  onNavigateToSubmit?: () => void
  currentRole?: Role
  currentUser?: UserProfile
}

export function ComplaintsPage({
  complaints,
  onOpen,
  onStatus,
  onAddComplaint,
  onNavigateToSubmit,
  currentRole = 'Admin',
  currentUser,
}: ComplaintsPageProps) {
  const [q, setQ] = useState('')
  const [bureau, setBureau] = useState('All')
  const [status, setStatus] = useState('All')
  const [priority, setPriority] = useState('All')
  const [complainant, setComplainant] = useState('All')
  const [officerFilter, setOfficerFilter] = useState('All')

  // Scoped list based on demo role
  const roleScopedComplaints = complaints.filter((c) => {
    if (currentRole === 'Complainant') {
      // Citizen sees their own complaints, student grievances, or any grievance submitted by them in session
      return (
        c.complainantEmail?.toLowerCase() === currentUser?.email?.toLowerCase() ||
        c.complainantName?.toLowerCase() === currentUser?.name?.toLowerCase() ||
        c.complainantType === 'Student' ||
        c.timeline?.some(
          (t) =>
            t.role === 'Complainant' &&
            (t.by?.toLowerCase().includes(currentUser?.name?.toLowerCase() || '') ||
              t.by?.toLowerCase().includes('complainant') ||
              t.by?.toLowerCase().includes('citizen'))
        )
      )
    }
    if (currentRole === 'Officer') {
      // Officers default to their assigned bureau or assigned officer
      if (officerFilter === 'MyAssigned') {
        return c.officer === currentUser?.name
      }
      return true
    }
    if (currentRole === 'BureauAdmin') {
      // Bureau admin focus
      return bureau === 'All' ? true : c.bureau === bureau
    }
    return true
  })

  const filtered = roleScopedComplaints.filter((c) => {
    const inst = institutions.find((i) => i.id === c.institutionId)
    const text = `${c.id} ${c.title} ${c.category} ${c.officer} ${c.institutionPermanentId || ''} ${inst?.name || ''} ${inst?.city || ''}`.toLowerCase()
    const matchesSearch = !q.trim() || text.includes(q.toLowerCase().trim())
    const matchesBureau = bureau === 'All' || c.bureau === bureau
    const matchesStatus = status === 'All' || c.status === status
    const matchesPriority = priority === 'All' || c.priority === priority
    const matchesComplainant = complainant === 'All' || c.complainantType === complainant
    const matchesOfficer = officerFilter === 'All' || officerFilter === 'MyAssigned' || c.officer === officerFilter
    return matchesSearch && matchesBureau && matchesStatus && matchesPriority && matchesComplainant && matchesOfficer
  })

  const resetFilters = () => {
    setQ('')
    setBureau('All')
    setStatus('All')
    setPriority('All')
    setComplainant('All')
    setOfficerFilter('All')
  }

  const exportCSV = () => {
    const headers = [
      'Case ID',
      'Permanent ID',
      'Institution',
      'Bureau',
      'Category',
      'Priority',
      'Officer',
      'Status',
      'Date',
      'Due Date',
    ]
    const rows = filtered.map((c) => [
      c.id,
      `"${c.institutionPermanentId || ''}"`,
      `"${instName(c.institutionId)}"`,
      c.bureau,
      `"${c.category}"`,
      c.priority,
      `"${c.officer}"`,
      c.status,
      c.date,
      c.due,
    ])
    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `AICTE-Complaints-${TODAY}.csv`
    a.click()
  }

  return (
    <div className="space-y-6">
      <PageTitle
        title={
          currentRole === 'Complainant'
            ? 'My Filed Grievances & Dockets'
            : currentRole === 'Officer'
            ? 'Officer Grievance Worklist'
            : 'All Complaints Directory'
        }
        sub={
          currentRole === 'Complainant'
            ? 'Review the status, official timelines, and documentation for grievances filed under your account'
            : 'Consolidated database of institution grievances, regulatory violations, and active inquiries'
        }
        tag={currentRole === 'Complainant' ? 'Citizen Portal' : 'AICTE Master Directory'}
        action={
          <div className="flex flex-wrap items-center gap-2">
            {onNavigateToSubmit && (
              <Button
                variant="primary"
                size="sm"
                onClick={onNavigateToSubmit}
                className="text-xs"
              >
                <FilePlus size={14} />
                <span>
                  {currentRole === 'Complainant' ? 'File New Grievance' : 'Register New Case'}
                </span>
              </Button>
            )}
            {currentRole !== 'Complainant' && (
              <Button variant="outline" size="sm" onClick={exportCSV} className="text-xs text-slate-700">
                <Download size={14} />
                <span>Export CSV</span>
              </Button>
            )}
          </div>
        }
      />

      {/* Role-Specific Context Notice */}
      {currentRole === 'Complainant' && (
        <Card className="border-l-4 border-l-emerald-600 bg-emerald-50/40 p-4">
          <div className="flex items-start gap-3">
            <UserCheck size={18} className="text-emerald-700 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-emerald-950 space-y-1">
              <div className="font-bold">Citizen Perspective: Personal Grievance Docket Access</div>
              <p className="text-emerald-900/80 leading-relaxed">
                You are viewing grievances registered by your account ({currentUser?.name}). You may track inquiry milestones, submit supplementary information, and access permitted public orders. Internal administrative records remain protected.
              </p>
            </div>
          </div>
        </Card>
      )}

      {currentRole === 'Officer' && (
        <Card className="border-l-4 border-l-teal-600 bg-teal-50/40 p-4">
          <div className="flex items-start gap-3">
            <UserCog size={18} className="text-teal-700 mt-0.5 flex-shrink-0" />
            <div className="text-xs text-teal-950 space-y-1">
              <div className="font-bold">Officer Perspective: Assigned Dockets ({currentUser?.name})</div>
              <p className="text-teal-900/80 leading-relaxed">
                As the designated investigating officer, you can log scrutiny remarks, upload inquiry memos, update permitted statuses, and review potential overlaps with parallel bureau filings.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Filters and Search Bar */}
      <Card padding="p-4">
        <div className="space-y-3">
          <div className="grid gap-3 md:grid-cols-12">
            <div className="md:col-span-4">
              <SearchBox
                value={q}
                onChange={setQ}
                placeholder="Search Case ID, Permanent ID, Institute, Category..."
              />
            </div>

            {currentRole !== 'Complainant' && (
              <div className="md:col-span-2">
                <select
                  value={bureau}
                  onChange={(e) => setBureau(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
                >
                  <option value="All">All Bureaus</option>
                  {BUREAUS.map((b) => (
                    <option key={b} value={b}>
                      {b} Bureau
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className={currentRole === 'Complainant' ? 'md:col-span-4' : 'md:col-span-2'}>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              >
                <option value="All">All Statuses</option>
                {STATUSES.map((s) => (
                  <option key={s} value={s}>
                    Status: {s}
                  </option>
                ))}
              </select>
            </div>

            <div className={currentRole === 'Complainant' ? 'md:col-span-4' : 'md:col-span-2'}>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
              >
                <option value="All">All Priorities</option>
                <option value="Critical">Critical Priority</option>
                <option value="High">High Priority</option>
                <option value="Medium">Medium Priority</option>
                <option value="Low">Low Priority</option>
              </select>
            </div>

            {currentRole !== 'Complainant' && (
              <div className="md:col-span-2">
                <select
                  value={officerFilter}
                  onChange={(e) => setOfficerFilter(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-700 shadow-2xs focus:border-navy-600 focus:outline-none"
                >
                  <option value="All">All Officers</option>
                  {currentRole === 'Officer' && (
                    <option value="MyAssigned">Assigned to Me ({currentUser?.name})</option>
                  )}
                  {OFFICERS.map((o) => (
                    <option key={o} value={o}>
                      Officer: {o}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-100 pt-3 text-xs text-slate-500">
            <span>
              Showing <strong>{filtered.length}</strong> of <strong>{roleScopedComplaints.length}</strong>{' '}
              {currentRole === 'Complainant' ? 'personal complaints' : 'total files'}
            </span>
            {(q || bureau !== 'All' || status !== 'All' || priority !== 'All' || complainant !== 'All' || officerFilter !== 'All') && (
              <button
                onClick={resetFilters}
                className="flex items-center gap-1 font-semibold text-teal-700 hover:underline"
              >
                <RotateCcw size={12} />
                <span>Reset Filters</span>
              </button>
            )}
          </div>
        </div>
      </Card>

      {/* Main Table */}
      <ComplaintTable
        rows={filtered}
        onOpen={onOpen}
        onStatus={(id, s) => onStatus(id, s)}
        currentRole={currentRole}
        currentUser={currentUser}
      />
    </div>
  )
}

/* =========================================================================
   FEATURE 3: Validated Complaint Submission Form & Confirmation Receipt
   ========================================================================= */

interface SubmitComplaintProps {
  complaints: Complaint[]
  onSubmit: (newComplaint: Complaint) => void
  onCancel: () => void
  onTrackCase: (caseId: string) => void
  currentRole?: Role
  currentUser?: UserProfile
}

export function SubmitComplaint({
  complaints,
  onSubmit,
  onCancel,
  onTrackCase,
  currentRole = 'Complainant',
  currentUser,
}: SubmitComplaintProps) {
  // Institution selection
  const [permanentIdInput, setPermanentIdInput] = useState(institutions[0].aicteId)
  const [selectedInstId, setSelectedInstId] = useState(institutions[0].id)
  const [instNameInput, setInstNameInput] = useState(institutions[0].name)
  const [instCityInput, setInstCityInput] = useState(institutions[0].city)
  const [instStateInput, setInstStateInput] = useState(institutions[0].state)
  const [instTypeInput, setInstTypeInput] = useState(institutions[0].type)

  // Complainant profile
  const [complainantType, setComplainantType] = useState<
    'Student' | 'Faculty' | 'Parent' | 'Whistleblower' | 'General Public'
  >(currentRole === 'Complainant' ? 'Student' : 'General Public')
  const [complainantName, setComplainantName] = useState(currentUser?.name || 'Rohit Sharma')
  const [complainantEmail, setComplainantEmail] = useState(
    currentUser?.email || 'rohit.sharma@student.edu.in'
  )
  const [complainantPhone, setComplainantPhone] = useState(currentUser?.phone || '+91 98765 43210')

  // Grievance particulars
  const [category, setCategory] = useState('Fee Regulation')
  const [bureau, setBureau] = useState<Bureau>('PGRC')
  const [priority, setPriority] = useState<Priority>('High')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')

  // Document upload state
  const [attachedFiles, setAttachedFiles] = useState<CaseDocument[]>([])
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [docVisibility, setDocVisibility] = useState<'Public' | 'Internal'>('Public')

  // Duplicate acknowledgement
  const [duplicateAcknowledged, setDuplicateAcknowledged] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  // Submission result state
  const [submittedCase, setSubmittedCase] = useState<Complaint | null>(null)

  // Handle Permanent ID lookup
  const handleSelectInstitution = (instId: string) => {
    const found = institutions.find((i) => i.id === instId)
    if (found) {
      setSelectedInstId(found.id)
      setPermanentIdInput(found.aicteId)
      setInstNameInput(found.name)
      setInstCityInput(found.city)
      setInstStateInput(found.state)
      setInstTypeInput(found.type)
    }
  }

  const handlePermanentIdChange = (pid: string) => {
    setPermanentIdInput(pid)
    const matched = institutions.find((i) => i.aicteId.toLowerCase() === pid.trim().toLowerCase())
    if (matched) {
      setSelectedInstId(matched.id)
      setInstNameInput(matched.name)
      setInstCityInput(matched.city)
      setInstStateInput(matched.state)
      setInstTypeInput(matched.type)
    }
  }

  // Auto suggest Bureau when Category changes
  const handleCategoryChange = (cat: string) => {
    setCategory(cat)
    if (cat.includes('Fee') || cat.includes('Ragging') || cat.includes('Harassment')) {
      setBureau('PGRC')
    } else if (cat.includes('Unapproved') || cat.includes('Faculty') || cat.includes('Admission')) {
      setBureau('RB')
    } else if (cat.includes('Infrastructure') || cat.includes('Facility')) {
      setBureau('Approval')
    } else if (cat.includes('Curriculum') || cat.includes('Syllabus')) {
      setBureau('Academic')
    } else if (cat.includes('Stipend') || cat.includes('Skill')) {
      setBureau('SB')
    }
  }

  // Accidental duplicate detection check
  const potentialDuplicates = complaints.filter((c) => {
    const sameInst =
      c.institutionId === selectedInstId ||
      (c.institutionPermanentId && c.institutionPermanentId === permanentIdInput.trim())
    const openStatus = c.status === 'Pending' || c.status === 'In Progress' || c.status === 'Escalated'
    const sameCategory = c.category.toLowerCase() === category.toLowerCase()
    const similarTitle =
      title.length > 5 &&
      c.title
        .toLowerCase()
        .split(' ')
        .filter((w) => w.length > 4)
        .some((word) => title.toLowerCase().includes(word))

    return sameInst && openStatus && (sameCategory || similarTitle)
  })

  // Handle file selection with validation
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null)
    const files = e.target.files
    if (!files || files.length === 0) return

    const file = files[0]
    const validExtensions = ['.pdf', '.jpg', '.jpeg', '.png', '.docx']
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()

    if (!validExtensions.includes(ext)) {
      setUploadError('Invalid file format. Permitted document formats: PDF, JPG, PNG, DOCX.')
      return
    }

    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File exceeds 10 MB limit. Please compress or select a smaller attachment.')
      return
    }

    const sizeKb = Math.round(file.size / 1024)
    const sizeStr = sizeKb > 1024 ? `${(sizeKb / 1024).toFixed(1)} MB` : `${sizeKb} KB`

    const newDoc: CaseDocument = {
      id: `doc-${Date.now()}-${Math.floor(Math.random() * 1000)}`,
      name: file.name,
      size: sizeStr,
      uploadDate: TODAY,
      uploadedBy: `${complainantName} (${currentRole})`,
      uploaderRole: currentRole,
      visibility: currentRole === 'Complainant' ? 'Public' : docVisibility,
      fileType: file.type || 'application/pdf',
    }

    setAttachedFiles((prev) => [...prev, newDoc])
    e.target.value = ''
  }

  const handleRemoveFile = (docId: string) => {
    setAttachedFiles((prev) => prev.filter((d) => d.id !== docId))
  }

  // Form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim() || title.trim().length < 10) {
      setFormError('Subject/Title must be at least 10 characters long.')
      return
    }
    if (!description.trim() || description.trim().length < 30) {
      setFormError('Description must be at least 30 characters long to provide sufficient investigation facts.')
      return
    }

    if (potentialDuplicates.length > 0 && !duplicateAcknowledged) {
      setFormError('Please check the acknowledgment box above regarding the potential duplicate notice.')
      return
    }
    setFormError(null)

    // Generate unique Case ID ensuring collision avoidance
    const prefix = bureau === 'Approval' ? 'AB' : bureau === 'Academic' ? 'ACD' : bureau
    let candidateId = ''
    let attempts = 0
    do {
      const randomSuffix = Math.floor(1000 + Math.random() * 9000)
      candidateId = `${prefix}-2026-${randomSuffix}`
      attempts++
    } while (complaints.some((c) => c.id === candidateId) && attempts < 100)
    const newCaseId = candidateId

    // Calculate SLA due date
    const slaDays = priority === 'Critical' ? 3 : priority === 'High' ? 7 : priority === 'Medium' ? 14 : 21
    const dueDate = new Date()
    dueDate.setDate(dueDate.getDate() + slaDays)
    const dueStr = dueDate.toISOString().slice(0, 10)

    const defaultOfficer =
      bureau === 'RB' ? 'Anita Verma' : bureau === 'Approval' ? 'Suresh Patel' : 'Rajesh Kumar'

    const newCase: Complaint = {
      id: newCaseId,
      institutionId: selectedInstId,
      institutionPermanentId: permanentIdInput.trim() || institutions[0].aicteId,
      bureau,
      category,
      priority,
      officer: defaultOfficer,
      status: 'Pending',
      date: TODAY,
      due: dueStr,
      title: title.trim(),
      description: description.trim(),
      complainantType,
      complainantName: complainantName.trim() || currentUser?.name || 'Citizen Complainant',
      complainantEmail: complainantEmail.trim() || currentUser?.email || 'citizen@gov.in',
      complainantPhone: complainantPhone.trim(),
      attachmentsCount: attachedFiles.length,
      documents: attachedFiles,
      timeline: [
        {
          label: 'Grievance submitted via AICTE Abhigyan Portal',
          date: `${TODAY} 10:45`,
          by: `${complainantName.trim()} (${complainantType})`,
          role: currentRole,
          note: 'Portal intake verified; acknowledgement issued to complainant.',
        },
        {
          label: `Assigned to ${defaultOfficer} (${bureau} Bureau)`,
          date: `${TODAY} 10:45`,
          by: 'Central Allocation Engine',
          role: 'Admin',
          note: `Automated routing based on category: ${category}. Target statutory SLA: ${slaDays} days.`,
        },
      ],
      assignments: [
        {
          officer: defaultOfficer,
          date: TODAY,
          by: 'Central Allocation Engine',
          byRole: 'Admin',
          previousOfficer: 'Intake Registration Cell',
          reason: `Initial category-based statutory case allocation to ${bureau} Bureau.`,
          bureau,
          type: 'initial',
        },
      ],
      nextAction: `Jurisdiction verification and preliminary scrutiny by ${bureau} Cell`,
      lastActionDate: TODAY,
    }

    onSubmit(newCase)
    setSubmittedCase(newCase)
  }

  // Confirmation Receipt Screen
  if (submittedCase) {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <Card className="border-t-4 border-t-emerald-600 p-8 text-center bg-white shadow-md">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 shadow-inner">
            <CheckCircle2 size={36} />
          </div>

          <span className="inline-block mt-4 px-3 py-1 rounded bg-emerald-100 text-emerald-800 text-xs font-bold font-mono">
            Acknowledgement Receipt Generated
          </span>

          <h2 className="mt-2 text-2xl font-bold text-slate-900">
            Grievance Docket Registered Successfully
          </h2>
          <p className="mt-1 text-xs text-slate-600 max-w-lg mx-auto">
            Your grievance file has been officially ingested into the AICTE Abhigyan System. An acknowledgement notice has been dispatched to{' '}
            <strong>{submittedCase.complainantEmail}</strong>.
          </p>

          {/* Official Docket Details Card */}
          <div className="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-5 text-left space-y-3">
            <div className="flex flex-wrap items-center justify-between border-b border-slate-200/80 pb-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                  Unique AICTE Case Reference ID
                </span>
                <div className="text-xl font-bold font-mono text-navy-900 mt-0.5">
                  {submittedCase.id}
                </div>
              </div>
              <div className="text-right">
                <Badge v={submittedCase.bureau} />
                <div className="text-[10px] text-slate-400 mt-1 font-mono">
                  Filed: {fmt(submittedCase.date)}
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 text-xs">
              <div>
                <span className="text-slate-500">Permanent Institution ID:</span>
                <div className="font-mono font-bold text-slate-900">
                  {submittedCase.institutionPermanentId}
                </div>
              </div>
              <div>
                <span className="text-slate-500">Accredited Campus:</span>
                <div className="font-semibold text-slate-900">
                  {instName(submittedCase.institutionId)}
                </div>
              </div>
              <div>
                <span className="text-slate-500">Allocated Bureau Jurisdiction:</span>
                <div className="font-semibold text-slate-900">
                  {submittedCase.bureau} ({BUREAU_INFO[submittedCase.bureau]?.name})
                </div>
              </div>
              <div>
                <span className="text-slate-500">Configured Statutory SLA Window:</span>
                <div className="font-semibold text-amber-700">
                  Due by {fmt(submittedCase.due)}
                </div>
              </div>
              <div>
                <span className="text-slate-500">Subject:</span>
                <div className="font-medium text-slate-900 truncate">{submittedCase.title}</div>
              </div>
              <div>
                <span className="text-slate-500">Supporting Evidence Attached:</span>
                <div className="font-medium text-slate-900">
                  {submittedCase.documents?.length || 0} Documents
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={() => onTrackCase(submittedCase.id)}
              className="text-xs"
            >
              <Eye size={14} />
              <span>Track Docket Lifecycle</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setSubmittedCase(null)
                setTitle('')
                setDescription('')
                setAttachedFiles([])
                setDuplicateAcknowledged(false)
              }}
              className="text-xs text-slate-700"
            >
              <FilePlus size={14} />
              <span>Submit Another Grievance</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={onCancel} className="text-xs text-slate-600">
              <span>Return to Directory</span>
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div>
          <h2 className="text-lg font-bold text-slate-900">
            {currentRole === 'Complainant'
              ? 'Lodge Formal Institutional Grievance'
              : 'Register New Complaint File'}
          </h2>
          <p className="text-xs text-slate-500">
            AICTE statutory grievance registration with permanent institution verification and duplicate detection
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onCancel} className="text-xs">
          <ArrowLeft size={13} />
          <span>Back</span>
        </Button>
      </div>

      {/* Legal & Demonstration Advisory */}
      <Card className="border-l-4 border-l-navy-800 bg-navy-50/40 p-4">
        <div className="flex items-start gap-3">
          <Shield size={18} className="text-navy-700 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-navy-950 space-y-1">
            <div className="font-bold">Official Statutory Redressal Mechanism</div>
            <p className="text-slate-600 leading-relaxed">
              Complaints submitted are audited across the Regulation Bureau (RB) and Public Grievance Redressal Cell (PGRC). False affidavits or frivolous claims are subject to statutory scrutiny under AICTE regulations.
            </p>
          </div>
        </div>
      </Card>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Section 1: Institution Permanent Identification */}
        <Card>
          <CardHeader
            title="1. Technical Campus &amp; Permanent ID Verification"
            sub="Link to stable AICTE Permanent Institute ID to aggregate historical records"
          />

          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Registered Institution *
                </label>
                <select
                  value={selectedInstId}
                  onChange={(e) => handleSelectInstitution(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                >
                  {institutions.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.name} ({i.city}, {i.state})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  AICTE Permanent Institution ID (PID) *
                </label>
                <input
                  type="text"
                  required
                  value={permanentIdInput}
                  onChange={(e) => handlePermanentIdChange(e.target.value)}
                  placeholder="e.g. 1-4821039"
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-mono font-bold text-slate-900 focus:border-navy-600 focus:outline-none"
                />
              </div>
            </div>

            {/* Readonly Campus Profile Snapshot */}
            <div className="rounded-lg bg-slate-50 p-3.5 border border-slate-200 text-xs grid gap-2 sm:grid-cols-3">
              <div>
                <span className="text-slate-500 block">Campus Name:</span>
                <span className="font-bold text-slate-800">{instNameInput}</span>
              </div>
              <div>
                <span className="text-slate-500 block">Location:</span>
                <span className="font-medium text-slate-800">
                  {instCityInput}, {instStateInput}
                </span>
              </div>
              <div>
                <span className="text-slate-500 block">Accreditation Category:</span>
                <span className="font-medium text-slate-800">{instTypeInput}</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Potential Duplicate Warning Banner */}
        {potentialDuplicates.length > 0 && (
          <Card className="border-l-4 border-l-amber-500 bg-amber-50/50 p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-amber-700 mt-0.5 flex-shrink-0" />
              <div className="space-y-2 text-xs text-amber-950 w-full">
                <div className="font-bold text-sm">Potential Duplicate Grievance Detected</div>
                <p className="leading-relaxed">
                  Our surveillance engine detected{' '}
                  <strong>{potentialDuplicates.length} active docket(s)</strong> already filed against{' '}
                  <strong>{instNameInput}</strong> under the same classification or related keywords:
                </p>

                <div className="space-y-1.5 pt-1">
                  {potentialDuplicates.slice(0, 2).map((dup) => (
                    <div
                      key={dup.id}
                      className="rounded bg-white p-2.5 border border-amber-200 flex items-center justify-between"
                    >
                      <div>
                        <span className="font-mono font-bold text-navy-900">{dup.id}</span>
                        <span className="text-slate-600 ml-2 font-medium">{dup.title}</span>
                      </div>
                      <Badge v={dup.status} />
                    </div>
                  ))}
                </div>

                <div className="pt-2 flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="dup-check"
                    checked={duplicateAcknowledged}
                    onChange={(e) => setDuplicateAcknowledged(e.target.checked)}
                    className="rounded border-slate-300 text-teal-600 focus:ring-teal-500 h-4 w-4"
                  />
                  <label htmlFor="dup-check" className="font-semibold text-amber-900 cursor-pointer">
                    I confirm this grievance relates to a separate occurrence, distinct batch, or new violation.
                  </label>
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Section 2: Complainant Identification */}
        <Card>
          <CardHeader
            title="2. Complainant Registry &amp; Affiliation"
            sub="Official contact details for statutory communications and hearing notices"
          />

          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Complainant Affiliation *
              </label>
              <select
                value={complainantType}
                onChange={(e) => setComplainantType(e.target.value as any)}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              >
                <option value="Student">Enrolled Student</option>
                <option value="Parent">Parent / Guardian</option>
                <option value="Faculty">Faculty Member</option>
                <option value="Whistleblower">Anonymous Whistleblower</option>
                <option value="General Public">General Citizen</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={complainantName}
                onChange={(e) => setComplainantName(e.target.value)}
                placeholder="Full Legal Name"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Email Address *
              </label>
              <input
                type="email"
                required
                value={complainantEmail}
                onChange={(e) => setComplainantEmail(e.target.value)}
                placeholder="name@domain.com"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Contact Phone
              </label>
              <input
                type="tel"
                value={complainantPhone}
                onChange={(e) => setComplainantPhone(e.target.value)}
                placeholder="+91 XXXXX XXXXX"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>
          </div>
        </Card>

        {/* Section 3: Grievance Classification & Substance */}
        <Card>
          <CardHeader
            title="3. Grievance Substance &amp; Classification"
            sub="Specific violations, regulatory citations, and institutional evidence"
          />

          <div className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Grievance Category *
                </label>
                <select
                  value={category}
                  onChange={(e) => handleCategoryChange(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                >
                  <option value="Fee Regulation">Fee Regulation &amp; Unauthorised Charges</option>
                  <option value="Harassment & Ragging">Anti-Ragging &amp; Student Safety</option>
                  <option value="Infrastructure">Infrastructure Deficit &amp; Safety</option>
                  <option value="Unapproved Courses">Unapproved Courses &amp; Bogus Programs</option>
                  <option value="Faculty Shortage">Faculty Shortage &amp; Cadre Ratio</option>
                  <option value="Admission Irregularity">Admission &amp; Counseling Irregularities</option>
                  <option value="Skill Certification">NEAT / Apprenticeship Stipend Deduction</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target AICTE Bureau *
                </label>
                <select
                  value={bureau}
                  onChange={(e) => setBureau(e.target.value as Bureau)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                >
                  {BUREAUS.map((b) => (
                    <option key={b} value={b}>
                      {b} Bureau ({BUREAU_INFO[b]?.name})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Priority / Statutory Urgency *
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as Priority)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                >
                  <option value="Critical">Critical (3-Day Emergency Window)</option>
                  <option value="High">High (7-Day Inquiry Window)</option>
                  <option value="Medium">Medium (14-Day Standard Window)</option>
                  <option value="Low">Low (21-Day Routine Window)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Grievance Subject / Docket Title * (Min. 10 chars)
              </label>
              <input
                type="text"
                required
                minLength={10}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Unapproved collection of Rs 35,000 under mandatory development charges"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Detailed Statement of Facts &amp; Allegations * (Min. 30 chars)
              </label>
              <textarea
                required
                minLength={30}
                rows={5}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Provide comprehensive details: department, affected batch, specific notice numbers, receipts issued, dates of representation made to management, and relief sought..."
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none leading-relaxed"
              />
            </div>
          </div>
        </Card>

        {/* Section 4: Supporting Evidence & Document Upload */}
        <Card>
          <CardHeader
            title="4. Supporting Documentation &amp; Evidence"
            sub="Attach affidavits, circulars, fee receipts, or communication records"
          />

          <div className="space-y-4">
            <div className="rounded-xl border-2 border-dashed border-slate-300 p-5 text-center bg-slate-50/60 hover:bg-slate-50 transition">
              <Upload size={24} className="mx-auto text-slate-400 mb-2" />
              <div className="text-xs font-semibold text-slate-800">
                Upload Supporting Exhibits &amp; Affidavits
              </div>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Supported formats: PDF, JPG, PNG, DOCX (Max 10 MB per file)
              </p>

              {currentRole !== 'Complainant' && (
                <div className="mt-2 inline-flex items-center gap-3 bg-white px-3 py-1 rounded-lg border border-slate-200 text-xs">
                  <span className="font-semibold text-slate-600">Access Scope:</span>
                  <label className="inline-flex items-center gap-1 cursor-pointer">
                    <input
                      type="radio"
                      name="visibility"
                      checked={docVisibility === 'Public'}
                      onChange={() => setDocVisibility('Public')}
                    />
                    <span>Public (Complainant Permitted)</span>
                  </label>
                  <label className="inline-flex items-center gap-1 cursor-pointer">
                    <input
                      type="radio"
                      name="visibility"
                      checked={docVisibility === 'Internal'}
                      onChange={() => setDocVisibility('Internal')}
                    />
                    <span>Internal Bureau Only</span>
                  </label>
                </div>
              )}

              <div className="mt-3">
                <label className="cursor-pointer rounded-lg bg-white border border-slate-300 px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-2xs hover:bg-slate-100 transition inline-block">
                  <span>Browse Local File</span>
                  <input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.png,.jpg,.jpeg,.docx"
                    className="hidden"
                  />
                </label>
              </div>

              {uploadError && (
                <div className="mt-2 text-xs font-semibold text-rose-600">{uploadError}</div>
              )}

              <div className="mt-2 text-[10px] text-slate-400">
                Demo Simulation: Files are held in browser session memory. No actual cloud upload occurs in this prototype.
              </div>
            </div>

            {/* List of Attached Documents */}
            {attachedFiles.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Attached Files ({attachedFiles.length}):
                </div>
                {attachedFiles.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between rounded-lg border border-slate-200 bg-white p-2.5 text-xs"
                  >
                    <div className="flex items-center gap-2.5 min-w-0">
                      <Paperclip size={14} className="text-teal-600 flex-shrink-0" />
                      <span className="font-semibold text-slate-800 truncate">{doc.name}</span>
                      <span className="text-[10px] text-slate-400 font-mono">({doc.size})</span>
                      <span
                        className={`text-[9px] px-1.5 py-0.2 rounded font-semibold ${
                          doc.visibility === 'Public'
                            ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                            : 'bg-slate-100 text-slate-700 border border-slate-200'
                        }`}
                      >
                        {doc.visibility}
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveFile(doc.id)}
                      className="text-slate-400 hover:text-rose-600 p-1 transition"
                      title="Remove file"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* Validation Error Banner */}
        {formError && (
          <div className="rounded-lg border border-rose-300 bg-rose-50 p-3 text-xs font-semibold text-rose-800 flex items-center gap-2">
            <AlertCircle size={16} className="text-rose-600 flex-shrink-0" />
            <span>{formError}</span>
          </div>
        )}

        {/* Submit Actions Bar */}
        <div className="flex items-center justify-end gap-3 border-t border-slate-200 pt-4">
          <Button type="button" variant="outline" size="sm" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" variant="primary" size="sm" className="px-6">
            <FilePlus size={14} />
            <span>Submit Official Grievance</span>
          </Button>
        </div>
      </form>
    </div>
  )
}

/* =========================================================================
   FEATURE 4: Case Tracking and Full Workflow Dossier (DetailsPage)
   ========================================================================= */

interface DetailsPageProps {
  complaint?: Complaint
  onBack: () => void
  onStatus: (id: string, s: Status, note?: string) => void
  onAssign: (id: string, o: string, reason?: string) => void
  onTransferBureau?: (id: string, newBureau: Bureau, newOfficer: string, reason: string) => void
  onRequestReassignment?: (
    id: string,
    request: Omit<ReassignmentRequest, 'id' | 'requestDate' | 'requestedBy' | 'requestedByRole' | 'status'>
  ) => void
  onReviewReassignmentRequest?: (
    id: string,
    requestId: string,
    decision: 'Approved' | 'Rejected',
    reviewNote?: string
  ) => void
  onAddNote?: (id: string, noteText: string) => void
  onAddDocument?: (id: string, doc: CaseDocument) => void
  onNavigateToInstitution?: (instId: string) => void
  currentRole?: Role
  currentUser?: UserProfile
}

export function DetailsPage({
  complaint: c,
  onBack,
  onStatus,
  onAssign,
  onTransferBureau,
  onRequestReassignment,
  onReviewReassignmentRequest,
  onAddNote,
  onAddDocument,
  onNavigateToInstitution,
  currentRole = 'Admin',
  currentUser,
}: DetailsPageProps) {
  const [newRemark, setNewRemark] = useState('')
  const [selectedOfficer, setSelectedOfficer] = useState(c?.officer || OFFICERS[0])
  const [isDocModalOpen, setIsDocModalOpen] = useState(false)
  const [docUploadName, setDocUploadName] = useState('')
  const [docUploadSize, setDocUploadSize] = useState('650 KB')
  const [docUploadVisibility, setDocUploadVisibility] = useState<'Public' | 'Internal'>('Public')
  const [statusRemarkModal, setStatusRemarkModal] = useState<Status | null>(null)
  const [statusRemarkText, setStatusRemarkText] = useState('')

  // Reassignment Modal state
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false)
  const [pendingOfficer, setPendingOfficer] = useState('')
  const [assignReason, setAssignReason] = useState('')

  // Cross-Bureau Transfer Modal state
  const [isTransferModalOpen, setIsTransferModalOpen] = useState(false)
  const [transferTargetBureau, setTransferTargetBureau] = useState<Bureau>(
    BUREAUS.find((b) => b !== c?.bureau) || 'RB'
  )
  const [transferTargetOfficer, setTransferTargetOfficer] = useState(
    getOfficersForBureau(BUREAUS.find((b) => b !== c?.bureau) || 'RB')[0] || OFFICERS[0]
  )
  const [transferReason, setTransferReason] = useState('')

  // Officer Request Reassignment / Transfer Modal state
  const [isRequestModalOpen, setIsRequestModalOpen] = useState(false)
  const [requestType, setRequestType] = useState<'officer' | 'bureau'>('officer')
  const [requestTargetBureau, setRequestTargetBureau] = useState<Bureau>(
    BUREAUS.find((b) => b !== c?.bureau) || 'RB'
  )
  const [requestTargetOfficer, setRequestTargetOfficer] = useState(
    getOfficersForBureau(c?.bureau || 'PGRC').find((o) => o !== c?.officer) || OFFICERS[0]
  )
  const [requestReason, setRequestReason] = useState('')

  // Review Reassignment Request Modal state
  const [reviewModal, setReviewModal] = useState<{
    request: ReassignmentRequest
    decision: 'Approved' | 'Rejected'
  } | null>(null)
  const [reviewNote, setReviewNote] = useState('')

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

  if (!c) {
    return (
      <Card className="p-8 text-center max-w-lg mx-auto my-12">
        <h3 className="text-base font-bold text-slate-900">Case Record Not Found</h3>
        <p className="mt-2 text-xs text-slate-600">The requested grievance docket could not be retrieved or no case was selected.</p>
        <div className="mt-4">
          <Button variant="primary" size="sm" onClick={onBack}>
            Return to Case Worklist
          </Button>
        </div>
      </Card>
    )
  }

  const inst = getInstitution(c.institutionId)
  const overdue = isOverdue(c)
  const daysRemaining = getDaysRemaining(c.due)

  // RBAC Permission checks
  const assignCheck = canAssignCase(currentUser, c)
  const transferCheck = canTransferBureau(currentUser, c)
  const remarkCheck = canAddCaseRemarks(currentUser, c)
  const docCheck = canUploadCaseDocument(currentUser, c)
  const reviewCheck = canReviewReassignmentRequest(currentUser, c)

  // Role-based document visibility
  const visibleDocuments = (c.documents || []).filter((doc) => {
    if (currentRole === 'Complainant') {
      return doc.visibility === 'Public'
    }
    return true
  })

  const handleAddRemark = (e: React.FormEvent) => {
    e.preventDefault()
    if (!newRemark.trim() || !onAddNote || !remarkCheck.allowed) return
    onAddNote(c.id, newRemark.trim())
    setNewRemark('')
  }

  const handleOfficerSelectChange = (officer: string) => {
    if (officer === c.officer) return
    setPendingOfficer(officer)
    setAssignReason('')
    setIsAssignModalOpen(true)
  }

  const handleConfirmAssignSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!pendingOfficer || !assignReason.trim()) return
    onAssign(c.id, pendingOfficer, assignReason.trim())
    setSelectedOfficer(pendingOfficer)
    setIsAssignModalOpen(false)
    setAssignReason('')
  }

  const handleOpenTransferModal = () => {
    const nextBureau = BUREAUS.find((b) => b !== c.bureau) || 'RB'
    setTransferTargetBureau(nextBureau)
    setTransferTargetOfficer(getOfficersForBureau(nextBureau)[0] || OFFICERS[0])
    setTransferReason('')
    setIsTransferModalOpen(true)
  }

  const handleBureauChangeInTransfer = (b: Bureau) => {
    setTransferTargetBureau(b)
    const officersInNewBureau = getOfficersForBureau(b)
    setTransferTargetOfficer(officersInNewBureau[0] || OFFICERS[0])
  }

  const handleConfirmTransferSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!transferReason.trim() || !onTransferBureau) return
    onTransferBureau(c.id, transferTargetBureau, transferTargetOfficer, transferReason.trim())
    setIsTransferModalOpen(false)
    setTransferReason('')
  }

  const handleOpenRequestModal = () => {
    setRequestType('officer')
    setRequestTargetOfficer(
      getOfficersForBureau(c.bureau).find((o) => o !== c.officer) || OFFICERS[0]
    )
    setRequestTargetBureau(BUREAUS.find((b) => b !== c.bureau) || 'RB')
    setRequestReason('')
    setIsRequestModalOpen(true)
  }

  const handleConfirmRequestSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!requestReason.trim() || !onRequestReassignment) return
    onRequestReassignment(c.id, {
      type: requestType,
      currentOfficer: c.officer,
      currentBureau: c.bureau,
      proposedOfficer: requestTargetOfficer,
      proposedBureau: requestType === 'bureau' ? requestTargetBureau : undefined,
      reason: requestReason.trim(),
    })
    setIsRequestModalOpen(false)
    setRequestReason('')
  }

  const handleConfirmReviewSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!reviewModal || !onReviewReassignmentRequest) return
    onReviewReassignmentRequest(
      c.id,
      reviewModal.request.id,
      reviewModal.decision,
      reviewNote.trim() || undefined
    )
    setReviewModal(null)
    setReviewNote('')
  }

  const handleUploadDocumentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!docUploadName.trim() || !onAddDocument || !docCheck.allowed) return

    const newDoc: CaseDocument = {
      id: `doc-${Date.now()}`,
      name: docUploadName.trim().endsWith('.pdf') ? docUploadName.trim() : `${docUploadName.trim()}.pdf`,
      size: docUploadSize || '750 KB',
      uploadDate: TODAY,
      uploadedBy: `${currentUser?.name || 'Officer'} (${currentRole})`,
      uploaderRole: currentRole,
      visibility: currentRole === 'Complainant' ? 'Public' : docUploadVisibility,
      fileType: 'application/pdf',
    }

    onAddDocument(c.id, newDoc)
    setDocUploadName('')
    setIsDocModalOpen(false)
  }

  const handleConfirmStatusChange = () => {
    if (statusRemarkModal) {
      onStatus(c.id, statusRemarkModal, statusRemarkText.trim() || undefined)
      setStatusRemarkModal(null)
      setStatusRemarkText('')
    }
  }

  // Allowed next statuses for current user
  const permittedStatuses =
    currentUser?.role === 'Admin'
      ? STATUSES.filter((s) => s !== c.status)
      : (PERMITTED_STATUS_TRANSITIONS[c.status] || []).filter(
          (s) => canUpdateCaseStatus(currentUser, c, s).allowed
        )

  return (
    <div className="space-y-6">
      {/* Top Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200/80 pb-3">
        <Button variant="outline" size="sm" onClick={onBack} className="text-xs">
          <ArrowLeft size={14} />
          <span>Back to Case Directory</span>
        </Button>

        {/* Permitted Status Update with RBAC Enforcement */}
        {currentRole !== 'Complainant' ? (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Advance Status:</span>
            {permittedStatuses.length > 0 ? (
              <select
                value={c.status}
                onChange={(e) => setStatusRemarkModal(e.target.value as Status)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-bold text-slate-800 shadow-2xs focus:border-navy-600 focus:outline-none"
              >
                <option value={c.status}>{c.status} (Current)</option>
                {permittedStatuses.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            ) : (
              <div className="flex items-center gap-1.5">
                <Badge v={c.status} />
                <span className="text-[10px] text-slate-500 font-medium bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                  {c.status === 'Resolved' ? 'Closed Docket' : 'No Permitted Transitions'}
                </span>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Official Case Status:</span>
            <Badge v={c.status} />
          </div>
        )}
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
                <span>
                  Complainant: {c.complainantName || c.complainantType || 'Enrolled Student'}
                </span>
              </span>
              <span className="flex items-center gap-1 font-mono font-semibold text-slate-700">
                <span>Permanent ID: {c.institutionPermanentId || inst?.aicteId}</span>
              </span>
            </div>

            {/* Next Scheduled Action Indicator */}
            <div className="mt-2 rounded-md bg-navy-50/70 p-2.5 border border-navy-100 text-xs">
              <span className="font-bold text-navy-900 uppercase text-[10px] tracking-wider block">
                Next Administrative Milestone:
              </span>
              <span className="text-slate-700 font-medium mt-0.5 block">
                {c.nextAction || 'Preliminary scrutiny verification and notice dispatch'}
              </span>
            </div>
          </div>

          {/* Quick SLA Badge Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-3 text-right shadow-2xs min-w-[170px]">
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
              Target Bureau: {c.bureau} Cell
            </div>
          </div>
        </div>
      </Card>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Complaint Narrative, Documents & Timeline */}
        <div className="space-y-6 lg:col-span-2">
          {/* Detailed Narrative */}
          <Card>
            <CardHeader
              title="Complaint Substance &amp; Allegations"
              sub="Official grievance statement filed on Abhigyan"
            />
            <div className="rounded-lg bg-slate-50/80 p-4 border border-slate-200/60 text-slate-800 text-sm leading-relaxed whitespace-pre-line">
              {c.description}
            </div>

            <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 border-t border-slate-100 pt-3">
              <div className="flex items-center gap-2">
                <Paperclip size={14} className="text-slate-400" />
                <span>
                  <strong>{visibleDocuments.length}</strong> Permitted Documents Available
                </span>
              </div>
              <span className="rounded bg-slate-100 px-2 py-0.5 text-slate-600 font-mono text-[11px]">
                Classification: {c.category}
              </span>
            </div>
          </Card>

          {/* Document Repository & Verification Exhibits */}
          <Card>
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Supporting Documentation &amp; Exhibits
                </h3>
                <p className="text-xs text-slate-500">
                  {currentRole === 'Complainant'
                    ? 'Publicly accessible filings and official notices'
                    : 'All filed exhibits, evidence circulars, and internal inquiry memos'}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsDocModalOpen(true)}
                className="text-xs"
              >
                <Upload size={13} />
                <span>
                  {currentRole === 'Complainant' ? 'Upload Evidence' : 'Attach Record'}
                </span>
              </Button>
            </div>

            <div className="space-y-2 mt-4">
              {visibleDocuments.map((doc) => (
                <div
                  key={doc.id}
                  className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-200 bg-white p-3 hover:bg-slate-50/60 transition"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-100 text-navy-800 flex-shrink-0">
                      <FileText size={17} />
                    </div>
                    <div className="min-w-0">
                      <div className="text-xs font-bold text-slate-900 truncate">{doc.name}</div>
                      <div className="text-[11px] text-slate-400">
                        <span>{doc.size}</span> • Uploaded {fmt(doc.uploadDate)} by{' '}
                        <span className="font-semibold text-slate-600">{doc.uploadedBy}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-semibold ${
                        doc.visibility === 'Public'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-slate-100 text-slate-700 border border-slate-200'
                      }`}
                    >
                      {doc.visibility === 'Public' ? 'Public / Permitted' : 'Internal Bureau Only'}
                    </span>
                    <button
                      onClick={() => alert(`Simulated document preview for: ${doc.name}\nSize: ${doc.size}\nVisibility: ${doc.visibility}`)}
                      className="p-1.5 text-slate-500 hover:text-navy-900 transition"
                      title="Preview Document"
                    >
                      <Eye size={15} />
                    </button>
                  </div>
                </div>
              ))}

              {visibleDocuments.length === 0 && (
                <div className="py-6 text-center text-xs text-slate-400">
                  No public supporting documents currently attached to this file.
                </div>
              )}
            </div>
          </Card>

          {/* Comprehensive Timeline Audit Trail */}
          <Card>
            <CardHeader
              title="Chronological Action History &amp; Audit Trail"
              sub="Timestamped log of status transitions, hearings, follow-up submissions, and notices"
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
                          {step.role && (
                            <span className="ml-1 text-[10px] bg-slate-100 text-slate-600 px-1.5 py-0.2 rounded">
                              {step.role}
                            </span>
                          )}
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

            {/* Follow-up / Additional Information Entry Form */}
            <form onSubmit={handleAddRemark} className="mt-6 border-t border-slate-100 pt-4">
              <label className="block text-xs font-bold text-slate-700 mb-1.5">
                {currentRole === 'Complainant'
                  ? 'Provide Additional Information / Follow-Up Statement:'
                  : 'Record Official Action / Investigation Milestone:'}
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newRemark}
                  onChange={(e) => setNewRemark(e.target.value)}
                  placeholder={
                    currentRole === 'Complainant'
                      ? 'e.g. Submitted latest fee notice issued by college on 24-Oct-2026...'
                      : 'e.g. Inquiry hearing scheduled; management issued show-cause notice...'
                  }
                  className="flex-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:border-navy-600 focus:outline-none"
                />
                <Button type="submit" variant="primary" size="sm" className="text-xs">
                  <Send size={13} />
                  <span>{currentRole === 'Complainant' ? 'Submit Update' : 'Log Entry'}</span>
                </Button>
              </div>
            </form>
          </Card>
        </div>

        {/* Right Column: Institution Info & Officer Assignment */}
        <div className="space-y-6">
          {/* Target Institution Profile Card */}
          <Card>
            <CardHeader
              title="Target Institution Profile"
              sub="Linked technical campus and regulatory records"
              action={
                onNavigateToInstitution &&
                currentRole !== 'Complainant' && (
                  <button
                    onClick={() => onNavigateToInstitution(c.institutionId)}
                    className="text-xs text-navy-700 font-semibold hover:underline flex items-center gap-1"
                  >
                    <span>Full Profile</span>
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
                    <span className="text-slate-500">Permanent Institution ID:</span>
                    <span className="font-mono font-bold text-slate-900">{inst.aicteId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Campus Category:</span>
                    <span className="font-medium text-slate-800">{inst.type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">First Approved Year:</span>
                    <span className="font-medium text-slate-800">{inst.approved}</span>
                  </div>
                  {currentRole !== 'Complainant' && (
                    <div className="flex justify-between">
                      <span className="text-slate-500">Institutional Risk Rating:</span>
                      <Badge v={`Risk: ${inst.riskLevel || 'Moderate'}`} />
                    </div>
                  )}
                </div>

                <div className="text-xs text-slate-500 pt-1">
                  Campus Registry Email:{' '}
                  <span className="font-medium text-slate-700">{inst.contactEmail}</span>
                </div>
              </div>
            ) : (
              <div className="text-xs text-slate-400">Institution details unavailable</div>
            )}
          </Card>

          {/* Assigned Officer & Case Management with Strict RBAC */}
          <Card>
            <CardHeader
              title={
                currentRole === 'Complainant'
                  ? 'Assigned Redressal Authority'
                  : 'Case Assignment & Jurisdiction'
              }
              sub={
                currentRole === 'Complainant'
                  ? 'Official cell managing your grievance'
                  : 'Designated bureau cell and assigned investigating officer'
              }
            />

            <div className="space-y-4">
              {/* Bureau Jurisdiction Status Box */}
              <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50/60 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-navy-800 text-white font-bold text-sm">
                  {currentRole === 'Complainant' ? 'AI' : c.officer.slice(0, 1)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-xs font-bold text-slate-900 truncate">
                      {currentRole === 'Complainant'
                        ? `${c.bureau} Grievance In-Charge`
                        : c.officer}
                    </h4>
                    <span className="text-[10px] text-teal-700 font-semibold bg-teal-50 px-2 py-0.5 rounded border border-teal-200 flex-shrink-0">
                      Active Docket
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">
                    Bureau: <strong>{c.bureau}</strong> ({BUREAU_INFO[c.bureau]?.name})
                  </div>
                </div>
              </div>

              {/* Administrative Jurisdiction Scope Status */}
              {currentRole !== 'Complainant' && (
                <div className="text-[11px] rounded-md p-2 border flex items-center justify-between gap-2 bg-slate-50 border-slate-200">
                  <span className="text-slate-600">Your Administrative Scope:</span>
                  <span className="font-semibold text-slate-800">
                    {currentRole === 'Admin'
                      ? 'System-Wide (All Bureaus)'
                      : currentRole === 'BureauAdmin'
                      ? `${currentUser?.bureau || 'PGRC'} Cell Admin`
                      : `Handling Officer (${currentUser?.bureau || 'PGRC'})`}
                  </span>
                </div>
              )}

              {/* Reassignment Controls for System Admin */}
              {currentRole === 'Admin' && (
                <div className="space-y-3 rounded-lg border border-slate-200 bg-slate-50/50 p-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-slate-800">
                      Reassign Responsible Officer:
                    </label>
                    <span className="text-[10px] text-indigo-700 font-medium">System Admin Authority</span>
                  </div>
                  <select
                    value={c.officer}
                    onChange={(e) => handleOfficerSelectChange(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                  >
                    {OFFICERS.map((off) => (
                      <option key={off} value={off}>
                        {off} {off === c.officer ? '(Current)' : ''}
                      </option>
                    ))}
                  </select>

                  <div className="pt-2 border-t border-slate-200/80 flex justify-between items-center">
                    <span className="text-[11px] text-slate-500">Cross-Jurisdiction Handover:</span>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleOpenTransferModal}
                      className="text-xs"
                    >
                      <span>Cross-Bureau Transfer</span>
                    </Button>
                  </div>
                </div>
              )}

              {/* Reassignment Controls for Bureau Admin */}
              {currentRole === 'BureauAdmin' && (
                <div className="space-y-3 rounded-lg border border-slate-200 bg-slate-50/50 p-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold text-slate-800">
                      Bureau Officer Reassignment:
                    </label>
                    <span className="text-[10px] text-teal-700 font-medium">
                      {currentUser?.bureau} Cell Jurisdiction
                    </span>
                  </div>

                  {assignCheck.allowed ? (
                    <>
                      <select
                        value={c.officer}
                        onChange={(e) => handleOfficerSelectChange(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white p-2 text-xs font-medium text-slate-800 focus:border-navy-600 focus:outline-none"
                      >
                        {getOfficersForBureau(c.bureau).map((off) => (
                          <option key={off} value={off}>
                            {off} {off === c.officer ? '(Current)' : ''}
                          </option>
                        ))}
                      </select>

                      <div className="pt-2 border-t border-slate-200/80 flex justify-between items-center">
                        <span className="text-[11px] text-slate-500">Transfer Out of {c.bureau}:</span>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={handleOpenTransferModal}
                          className="text-xs"
                        >
                          <span>Cross-Bureau Transfer</span>
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="rounded-lg bg-amber-50 p-2.5 border border-amber-200 text-xs text-amber-900 space-y-1">
                      <div className="font-bold flex items-center gap-1">
                        <Lock size={12} /> Assignment Restricted
                      </div>
                      <p className="text-[11px] leading-relaxed">
                        Docket belongs to <strong>{c.bureau}</strong>. As Bureau Admin for{' '}
                        <strong>{currentUser?.bureau}</strong>, you cannot assign officers or transfer this case directly.
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Workflow for Handling Officers */}
              {currentRole === 'Officer' && (
                <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-800">Officer Assignment Policy:</span>
                    <span className="text-[10px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">
                      Workflow Only
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-600 leading-relaxed">
                    Handling Officers cannot directly change the assigned Bureau/Cell or reassign cases to other officers. You can request reassignment or transfer through the official workflow.
                  </p>
                  <Button
                    type="button"
                    variant="primary"
                    size="sm"
                    onClick={handleOpenRequestModal}
                    className="w-full text-xs mt-1"
                  >
                    <span>Request Reassignment / Bureau Transfer</span>
                  </Button>
                </div>
              )}

              {/* Pending Requests on this Case */}
              {c.reassignmentRequests && c.reassignmentRequests.length > 0 && (
                <div className="rounded-lg border border-amber-200 bg-amber-50/40 p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-amber-950">
                      Reassignment / Transfer Requests:
                    </span>
                    <span className="text-[10px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.5 rounded">
                      {c.reassignmentRequests.filter((r) => r.status === 'Pending').length} Pending
                    </span>
                  </div>

                  <div className="space-y-2">
                    {c.reassignmentRequests.map((req) => (
                      <div
                        key={req.id}
                        className="rounded bg-white p-2.5 border border-amber-200/80 text-[11px] space-y-1.5 shadow-2xs"
                      >
                        <div className="flex items-center justify-between font-semibold">
                          <span className="text-slate-900">
                            {req.type === 'bureau' ? 'Cross-Bureau Transfer' : 'Officer Handover'}
                          </span>
                          <span
                            className={`rounded px-1.5 py-0.2 text-[10px] font-bold ${
                              req.status === 'Pending'
                                ? 'bg-amber-100 text-amber-800'
                                : req.status === 'Approved'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-rose-100 text-rose-800'
                            }`}
                          >
                            {req.status}
                          </span>
                        </div>
                        <div className="text-slate-600">
                          From: <strong>{req.requestedBy}</strong> ({req.requestedByRole})
                        </div>
                        <div className="text-slate-600">
                          Proposed:{' '}
                          <strong>
                            {req.type === 'bureau'
                              ? `${req.proposedBureau} Cell`
                              : req.proposedOfficer}
                          </strong>
                        </div>
                        <div className="text-slate-500 italic bg-slate-50 p-1.5 rounded">
                          &quot;{req.reason}&quot;
                        </div>

                        {req.status === 'Pending' && reviewCheck.allowed && (
                          <div className="pt-1.5 flex gap-1.5 justify-end border-t border-slate-100">
                            <button
                              type="button"
                              onClick={() => setReviewModal({ request: req, decision: 'Rejected' })}
                              className="px-2 py-1 text-[10px] font-bold rounded border border-rose-300 text-rose-700 hover:bg-rose-50"
                            >
                              Reject
                            </button>
                            <button
                              type="button"
                              onClick={() => setReviewModal({ request: req, decision: 'Approved' })}
                              className="px-2 py-1 text-[10px] font-bold rounded bg-teal-700 text-white hover:bg-teal-800"
                            >
                              Approve
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Assignment Audit Log */}
              <div className="border-t border-slate-100 pt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
                    Assignment &amp; Transfer Audit Log
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">
                    {c.assignments.length} Record(s)
                  </span>
                </div>
                <div className="space-y-2">
                  {c.assignments.map((a, idx) => (
                    <div
                      key={idx}
                      className="text-xs text-slate-700 bg-slate-50 p-2.5 rounded-lg border border-slate-200/70 space-y-1"
                    >
                      <div className="flex items-center justify-between font-semibold">
                        <span className="text-slate-900">
                          {a.type === 'transfer' ? (
                            <span>
                              Transfer: {a.previousBureau || 'Origin'} &rarr; {a.bureau || c.bureau}
                            </span>
                          ) : (
                            <span>
                              {a.previousOfficer ? `${a.previousOfficer} \u2192 ` : ''}
                              {a.officer}
                            </span>
                          )}
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">{fmt(a.date)}</span>
                      </div>
                      <div className="text-[11px] text-slate-500">
                        Authorized by: <strong className="text-slate-700">{a.by}</strong>
                        {a.byRole && (
                          <span className="ml-1 text-[10px] bg-slate-200 text-slate-700 px-1 py-0.2 rounded font-mono">
                            {a.byRole}
                          </span>
                        )}
                      </div>
                      {a.reason && (
                        <div className="text-[11px] text-slate-600 bg-white p-1.5 rounded border border-slate-100">
                          <span className="font-semibold text-slate-700">Reason:</span> {a.reason}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                <div className="mt-3 rounded bg-navy-50/60 p-2 text-[10px] text-navy-800 border border-navy-100">
                  <strong>FastAPI RBAC Security Notice:</strong> All assignment mutations and cross-Bureau handovers require authenticated administrative credentials. In production, policies are validated server-side with PostgreSQL chronological triggers.
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Officer Reassignment Confirmation & Reason Modal */}
      {isAssignModalOpen && (
        <Modal
          open={isAssignModalOpen}
          onClose={() => setIsAssignModalOpen(false)}
          title={`Reassign Docket ${c.id} to ${pendingOfficer}`}
        >
          <form onSubmit={handleConfirmAssignSubmit} className="space-y-4 text-xs">
            <p className="text-slate-600">
              You are reassigning investigating responsibility for docket <strong>{c.id}</strong> from{' '}
              <span className="font-bold text-slate-900">{c.officer}</span> to{' '}
              <span className="font-bold text-teal-800">{pendingOfficer}</span> within{' '}
              <strong>{c.bureau} Bureau</strong>.
            </p>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Mandatory Reassignment Reason / Justification *
              </label>
              <textarea
                required
                rows={3}
                value={assignReason}
                onChange={(e) => setAssignReason(e.target.value)}
                placeholder="e.g. Workload balancing; reallocated to subject matter expert for inspection..."
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">
                This reason will be permanently archived into the statutory audit trail.
              </span>
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsAssignModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="teal" size="sm">
                <CheckCircle2 size={13} />
                <span>Confirm &amp; Record Reassignment</span>
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Cross-Bureau Transfer Modal */}
      {isTransferModalOpen && (
        <Modal
          open={isTransferModalOpen}
          onClose={() => setIsTransferModalOpen(false)}
          title={`Initiate Cross-Bureau Transfer: Docket ${c.id}`}
        >
          <form onSubmit={handleConfirmTransferSubmit} className="space-y-4 text-xs">
            <p className="text-slate-600">
              Transfer case jurisdiction from <strong>{c.bureau} Cell</strong> to another administrative Bureau.
            </p>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Target Bureau *</label>
                <select
                  value={transferTargetBureau}
                  onChange={(e) => handleBureauChangeInTransfer(e.target.value as Bureau)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs font-semibold focus:border-navy-600 focus:outline-none"
                >
                  {BUREAUS.filter((b) => b !== c.bureau).map((b) => (
                    <option key={b} value={b}>
                      {b} - {BUREAU_INFO[b]?.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Designated Officer in Target Bureau *
                </label>
                <select
                  value={transferTargetOfficer}
                  onChange={(e) => setTransferTargetOfficer(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                >
                  {getOfficersForBureau(transferTargetBureau).map((off) => (
                    <option key={off} value={off}>
                      {off}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Statutory Reason for Cross-Bureau Transfer *
              </label>
              <textarea
                required
                rows={3}
                value={transferReason}
                onChange={(e) => setTransferReason(e.target.value)}
                placeholder="e.g. Investigation revealed building infrastructure violations outside PGRC mandate; statutory action falls under Approval Bureau."
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div className="rounded-lg bg-amber-50 p-2.5 text-[11px] text-amber-900 border border-amber-200">
              <strong>Statutory Record:</strong> Previous Bureau ({c.bureau}), New Bureau ({transferTargetBureau}), Actor ({currentUser?.name}), Timestamp, and Reason will be indelibly saved to the audit trail.
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsTransferModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm">
                <CheckCircle2 size={13} />
                <span>Execute Cross-Bureau Transfer</span>
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Handling Officer Request Reassignment / Transfer Modal */}
      {isRequestModalOpen && (
        <Modal
          open={isRequestModalOpen}
          onClose={() => setIsRequestModalOpen(false)}
          title={`Formal Reassignment / Transfer Request: ${c.id}`}
        >
          <form onSubmit={handleConfirmRequestSubmit} className="space-y-4 text-xs">
            <p className="text-slate-600">
              Handling Officers cannot directly change case jurisdiction. Submit a formal request to your Bureau Head and System Admin.
            </p>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Request Type *</label>
              <div className="grid grid-cols-2 gap-2">
                <label
                  className={`flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer ${
                    requestType === 'officer'
                      ? 'border-navy-800 bg-navy-50 font-bold text-navy-900'
                      : 'border-slate-200 bg-white text-slate-700'
                  }`}
                >
                  <input
                    type="radio"
                    name="reqType"
                    checked={requestType === 'officer'}
                    onChange={() => setRequestType('officer')}
                    className="accent-navy-800"
                  />
                  <span>Reassign Officer (Within {c.bureau})</span>
                </label>
                <label
                  className={`flex items-center gap-2 p-2.5 rounded-lg border cursor-pointer ${
                    requestType === 'bureau'
                      ? 'border-navy-800 bg-navy-50 font-bold text-navy-900'
                      : 'border-slate-200 bg-white text-slate-700'
                  }`}
                >
                  <input
                    type="radio"
                    name="reqType"
                    checked={requestType === 'bureau'}
                    onChange={() => setRequestType('bureau')}
                    className="accent-navy-800"
                  />
                  <span>Cross-Bureau Transfer</span>
                </label>
              </div>
            </div>

            {requestType === 'officer' ? (
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Proposed Officer in {c.bureau} Bureau:
                </label>
                <select
                  value={requestTargetOfficer}
                  onChange={(e) => setRequestTargetOfficer(e.target.value)}
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                >
                  {getOfficersForBureau(c.bureau)
                    .filter((o) => o !== c.officer)
                    .map((off) => (
                      <option key={off} value={off}>
                        {off}
                      </option>
                    ))}
                </select>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Proposed Bureau *</label>
                  <select
                    value={requestTargetBureau}
                    onChange={(e) => {
                      const b = e.target.value as Bureau
                      setRequestTargetBureau(b)
                      setRequestTargetOfficer(getOfficersForBureau(b)[0] || OFFICERS[0])
                    }}
                    className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                  >
                    {BUREAUS.filter((b) => b !== c.bureau).map((b) => (
                      <option key={b} value={b}>
                        {b} - {BUREAU_INFO[b]?.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Proposed Officer (Optional)
                  </label>
                  <select
                    value={requestTargetOfficer}
                    onChange={(e) => setRequestTargetOfficer(e.target.value)}
                    className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                  >
                    {getOfficersForBureau(requestTargetBureau).map((off) => (
                      <option key={off} value={off}>
                        {off}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Justification &amp; Statutory Grounds for Handover *
              </label>
              <textarea
                required
                rows={3}
                value={requestReason}
                onChange={(e) => setRequestReason(e.target.value)}
                placeholder="Explain why this case requires handover (e.g. institutional conflict of interest, technical jurisdiction mismatch, specialized inquiry required)..."
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsRequestModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm">
                <Send size={13} />
                <span>Submit Handover Request</span>
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Review Reassignment Request Modal (Admin / Bureau Admin) */}
      {reviewModal && (
        <Modal
          open={!!reviewModal}
          onClose={() => setReviewModal(null)}
          title={`${reviewModal.decision} Reassignment Request #${reviewModal.request.id}`}
        >
          <form onSubmit={handleConfirmReviewSubmit} className="space-y-4 text-xs">
            <p className="text-slate-600">
              You are deciding to{' '}
              <strong
                className={reviewModal.decision === 'Approved' ? 'text-emerald-700' : 'text-rose-700'}
              >
                {reviewModal.decision.toUpperCase()}
              </strong>{' '}
              the handover request submitted by <strong>{reviewModal.request.requestedBy}</strong>.
            </p>

            <div className="rounded-lg bg-slate-50 p-3 border border-slate-200 text-slate-700 space-y-1">
              <div>
                <strong>Type:</strong>{' '}
                {reviewModal.request.type === 'bureau' ? 'Cross-Bureau Transfer' : 'Officer Reassignment'}
              </div>
              <div>
                <strong>Reason given:</strong> &quot;{reviewModal.request.reason}&quot;
              </div>
              {reviewModal.request.proposedBureau && (
                <div>
                  <strong>Target Bureau:</strong> {reviewModal.request.proposedBureau}
                </div>
              )}
              {reviewModal.request.proposedOfficer && (
                <div>
                  <strong>Target Officer:</strong> {reviewModal.request.proposedOfficer}
                </div>
              )}
            </div>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Official Determination / Review Note:
              </label>
              <textarea
                rows={2}
                value={reviewNote}
                onChange={(e) => setReviewNote(e.target.value)}
                placeholder={
                  reviewModal.decision === 'Approved'
                    ? 'e.g. Approved following review of statutory jurisdiction and institutional remit.'
                    : 'e.g. Rejected; complaint remains within current bureau remit.'
                }
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setReviewModal(null)}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant={reviewModal.decision === 'Approved' ? 'teal' : 'primary'}
                size="sm"
              >
                <CheckCircle2 size={13} />
                <span>Confirm {reviewModal.decision}</span>
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Document Upload Modal */}
      {isDocModalOpen && (
        <Modal
          open={isDocModalOpen}
          onClose={() => setIsDocModalOpen(false)}
          title="Upload Supplementary Case Document"
        >
          <form onSubmit={handleUploadDocumentSubmit} className="space-y-4 text-xs">
            <p className="text-slate-600">
              Attach supporting exhibits, institutional notices, or inspection affidavits to docket{' '}
              <strong>{c.id}</strong>.
            </p>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">Document Title *</label>
              <input
                type="text"
                required
                value={docUploadName}
                onChange={(e) => setDocUploadName(e.target.value)}
                placeholder="e.g. Fee_Payment_Receipt_Batch_2026.pdf"
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Simulated Size</label>
                <input
                  type="text"
                  value={docUploadSize}
                  onChange={(e) => setDocUploadSize(e.target.value)}
                  placeholder="e.g. 1.2 MB"
                  className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                />
              </div>

              {currentRole !== 'Complainant' && (
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Visibility Scope</label>
                  <select
                    value={docUploadVisibility}
                    onChange={(e) => setDocUploadVisibility(e.target.value as any)}
                    className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
                  >
                    <option value="Public">Public (Complainant Permitted)</option>
                    <option value="Internal">Internal Bureau Only</option>
                  </select>
                </div>
              )}
            </div>

            <div className="rounded-lg bg-slate-50 p-3 text-[11px] text-slate-500 border border-slate-200">
              Files uploaded in this demo are processed in local session memory. Real storage with S3/GCS will be wired via FastAPI.
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setIsDocModalOpen(false)}
              >
                Cancel
              </Button>
              <Button type="submit" variant="primary" size="sm">
                <Upload size={13} />
                <span>Save to Docket</span>
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Status Advance Confirmation Modal */}
      {statusRemarkModal && (
        <Modal
          open={!!statusRemarkModal}
          onClose={() => setStatusRemarkModal(null)}
          title={`Confirm Status Transition to "${statusRemarkModal}"`}
        >
          <div className="space-y-4 text-xs">
            <p className="text-slate-600">
              You are advancing case <strong>{c.id}</strong> from{' '}
              <span className="font-bold text-slate-900">{c.status}</span> to{' '}
              <span className="font-bold text-teal-800">{statusRemarkModal}</span>.
            </p>

            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Official Justification / Milestone Remark (Optional):
              </label>
              <textarea
                rows={3}
                value={statusRemarkText}
                onChange={(e) => setStatusRemarkText(e.target.value)}
                placeholder="e.g. Compliance documents verified; show-cause order closed..."
                className="w-full rounded-lg border border-slate-300 p-2 text-xs focus:border-navy-600 focus:outline-none"
              />
            </div>

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setStatusRemarkModal(null)}
              >
                Cancel
              </Button>
              <Button type="button" variant="teal" size="sm" onClick={handleConfirmStatusChange}>
                <CheckCircle2 size={13} />
                <span>Confirm Transition</span>
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
