import { useState } from 'react'
import {
  AlertTriangle,
  Building2,
  CheckCircle2,
  ExternalLink,
  FileText,
  Mail,
  MapPin,
  Phone,
  Search,
  ShieldAlert,
} from 'lucide-react'
import type { Complaint, Role, Status, UserProfile } from '../types'
import { institutions } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle, SearchBox } from '../components/ui'
import ComplaintTable from '../components/ComplaintTable'

interface InstitutionsProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus?: (id: string, s: Status, note?: string) => void
  currentRole?: Role
  currentUser?: UserProfile
}

export default function Institutions({
  complaints,
  onOpen,
  onStatus,
  currentRole,
  currentUser,
}: InstitutionsProps) {
  const [q, setQ] = useState('')
  const [stateFilter, setStateFilter] = useState('All')
  const [typeFilter, setTypeFilter] = useState('All')
  const [selectedInstId, setSelectedInstId] = useState(institutions[0].id)

  const states = ['All', ...Array.from(new Set(institutions.map((i) => i.state)))]
  const types = ['All', ...Array.from(new Set(institutions.map((i) => i.type)))]

  const filtered = institutions.filter((i) => {
    const text = `${i.name} ${i.city} ${i.state} ${i.aicteId} ${i.type}`.toLowerCase()
    const matchesSearch = !q.trim() || text.includes(q.toLowerCase().trim())
    const matchesState = stateFilter === 'All' || i.state === stateFilter
    const matchesType = typeFilter === 'All' || i.type === typeFilter
    return matchesSearch && matchesState && matchesType
  })

  const currentInst = institutions.find((i) => i.id === selectedInstId) || institutions[0]
  const instComplaints = complaints.filter(
    (c) =>
      c.institutionId === currentInst.id ||
      (c.institutionPermanentId && c.institutionPermanentId === currentInst.aicteId)
  )
  const activeCount = instComplaints.filter((c) => c.status !== 'Resolved').length
  const resolvedCount = instComplaints.filter((c) => c.status === 'Resolved').length

  const bureauCounts: Record<string, number> = {}
  instComplaints.forEach((c) => {
    bureauCounts[c.bureau] = (bureauCounts[c.bureau] || 0) + 1
  })

  return (
    <div className="space-y-6">
      <PageTitle
        title="Institutions Roster &amp; Permanent ID Profiles"
        sub="Monitor complaint frequency, cross-bureau density, and regulatory adherence linked by stable Permanent Institution ID"
        tag="AICTE Registry"
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column: Search & Institution List */}
        <Card className="lg:col-span-1 space-y-4">
          <CardHeader
            title="Registered Technical Institutions"
            sub={`${filtered.length} campuses indexed by Permanent ID`}
          />

          <SearchBox
            value={q}
            onChange={setQ}
            placeholder="Search by name, city, AICTE PID..."
          />

          <div className="grid grid-cols-2 gap-2 text-xs">
            <select
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white p-2 text-xs text-slate-700 focus:outline-none"
            >
              {states.map((s) => (
                <option key={s} value={s}>
                  State: {s}
                </option>
              ))}
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="rounded-lg border border-slate-300 bg-white p-2 text-xs text-slate-700 focus:outline-none"
            >
              {types.map((t) => (
                <option key={t} value={t}>
                  Type: {t}
                </option>
              ))}
            </select>
          </div>

          <div className="max-h-[32rem] space-y-1.5 overflow-y-auto pr-1 scrollbar-thin">
            {filtered.map((inst) => {
              const complaintsForThis = complaints.filter(
                (c) =>
                  c.institutionId === inst.id ||
                  (c.institutionPermanentId && c.institutionPermanentId === inst.aicteId)
              )
              const hasActive = complaintsForThis.some((c) => c.status !== 'Resolved')
              const isSelected = selectedInstId === inst.id

              return (
                <button
                  key={inst.id}
                  onClick={() => setSelectedInstId(inst.id)}
                  className={`w-full rounded-xl p-3 text-left transition border ${
                    isSelected
                      ? 'border-navy-600 bg-navy-50/70 shadow-2xs ring-1 ring-navy-300'
                      : 'border-slate-200/80 bg-white hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">
                      {inst.name}
                    </h4>
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                        inst.riskLevel === 'High'
                          ? 'bg-rose-100 text-rose-700'
                          : inst.riskLevel === 'Moderate'
                          ? 'bg-amber-100 text-amber-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}
                    >
                      {inst.riskLevel || 'Low'}
                    </span>
                  </div>

                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-500">
                    <span className="flex items-center gap-1 font-mono text-[10px]">
                      PID: {inst.aicteId}
                    </span>
                    <span
                      className={`font-semibold ${
                        hasActive ? 'text-amber-700' : 'text-slate-500'
                      }`}
                    >
                      {complaintsForThis.length} Case{complaintsForThis.length !== 1 ? 's' : ''}
                    </span>
                  </div>
                </button>
              )
            })}

            {filtered.length === 0 && (
              <div className="py-10 text-center text-xs text-slate-400">
                No institutions match the filter criteria.
              </div>
            )}
          </div>
        </Card>

        {/* Right Column: Detailed Institution Profile & Linked Dossier */}
        <div className="space-y-6 lg:col-span-2">
          {/* Profile Card */}
          <Card className="border-t-4 border-t-navy-800">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="rounded-md bg-navy-100 px-2 py-0.5 font-mono text-xs font-bold text-navy-800">
                    PID: {currentInst.aicteId}
                  </span>
                  <Badge v={currentInst.type} />
                  <Badge v={`Risk: ${currentInst.riskLevel || 'Low'}`} />
                </div>
                <h2 className="text-xl font-bold text-slate-900 mt-1">{currentInst.name}</h2>
                <p className="text-xs text-slate-500 flex items-center gap-1.5">
                  <MapPin size={13} className="text-slate-400" />
                  <span>
                    {currentInst.city}, {currentInst.state} • Approved since {currentInst.approved}
                  </span>
                </p>
              </div>

              <div className="flex items-center gap-3">
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-center min-w-[80px]">
                  <div className="text-lg font-bold text-amber-700">{activeCount}</div>
                  <div className="text-[10px] uppercase font-bold text-slate-500">Active</div>
                </div>
                <div className="rounded-xl border border-slate-200 bg-slate-50 p-2.5 text-center min-w-[80px]">
                  <div className="text-lg font-bold text-emerald-700">{resolvedCount}</div>
                  <div className="text-[10px] uppercase font-bold text-slate-500">Resolved</div>
                </div>
              </div>
            </div>

            {/* Bureau Breakdown for this Institution */}
            <div className="mt-4 pt-3 border-t border-slate-100">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block mb-2">
                Cross-Bureau Case Distribution for this Permanent ID:
              </span>
              <div className="flex flex-wrap gap-2">
                {Object.keys(bureauCounts).length > 0 ? (
                  Object.entries(bureauCounts).map(([b, count]) => (
                    <div
                      key={b}
                      className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs"
                    >
                      <Badge v={b} />
                      <span className="font-bold text-slate-800">{count} docket(s)</span>
                    </div>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">No dockets registered for this campus.</span>
                )}
              </div>
            </div>

            {/* Quick Contact & Details grid */}
            <div className="mt-4 grid gap-3 sm:grid-cols-2 rounded-lg bg-slate-50/70 p-3.5 border border-slate-100 text-xs">
              <div className="flex items-center gap-2 text-slate-600">
                <Mail size={14} className="text-slate-400 flex-shrink-0" />
                <span className="truncate">{currentInst.contactEmail || 'office@institute.ac.in'}</span>
              </div>
              <div className="flex items-center gap-2 text-slate-600">
                <Phone size={14} className="text-slate-400 flex-shrink-0" />
                <span>{currentInst.contactPhone || '+91 11 2000 0000'}</span>
              </div>
            </div>
          </Card>

          {/* Associated Complaints Dossier */}
          <Card>
            <CardHeader
              title={`Consolidated Cases for Permanent ID: ${currentInst.aicteId}`}
              sub={`All ${instComplaints.length} complaints filed across Regulation Bureau, PGRC, Approval, and Academic bureaus`}
            />

            <ComplaintTable
              rows={instComplaints}
              onOpen={onOpen}
              onStatus={onStatus}
              currentRole={currentRole}
              currentUser={currentUser}
            />
          </Card>
        </div>
      </div>
    </div>
  )
}
