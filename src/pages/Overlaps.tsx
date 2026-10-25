import { useEffect, useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  Clock,
  ExternalLink,
  GitMerge,
  Info,
  Layers,
  PauseCircle,
  Shield,
  ShieldAlert,
  Sparkles,
  X,
} from 'lucide-react'
import type { Complaint, Overlap, Role, UserProfile } from '../types'
import { TODAY, fmt, instName, overlaps as initialOverlaps } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle } from '../components/ui'

const OVERLAP_STORAGE_KEYS = {
  STATES: 'abhigyan_overlap_states',
  NOTES: 'abhigyan_overlap_notes',
} as const

interface OverlapsProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  currentRole?: Role
  currentUser?: UserProfile
}

export default function Overlaps({
  complaints,
  onOpen,
  currentRole = 'Admin',
  currentUser,
}: OverlapsProps) {
  const [overlapStates, setOverlapStates] = useState<
    Record<string, 'linked' | 'dismissed' | 'deferred'>
  >(() => {
    try {
      const stored = localStorage.getItem(OVERLAP_STORAGE_KEYS.STATES)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch {
      // fallback
    }
    return {
      o2: 'linked',
      o4: 'linked',
      o5: 'dismissed',
    }
  })

  const [overlapNotes, setOverlapNotes] = useState<Record<string, string>>(() => {
    try {
      const stored = localStorage.getItem(OVERLAP_STORAGE_KEYS.NOTES)
      if (stored) {
        return JSON.parse(stored)
      }
    } catch {
      // fallback
    }
    return {}
  })

  const [tab, setTab] = useState<'open' | 'linked' | 'dismissed' | 'deferred'>('open')

  useEffect(() => {
    try {
      localStorage.setItem(OVERLAP_STORAGE_KEYS.STATES, JSON.stringify(overlapStates))
    } catch {
      // ignore
    }
  }, [overlapStates])

  useEffect(() => {
    try {
      localStorage.setItem(OVERLAP_STORAGE_KEYS.NOTES, JSON.stringify(overlapNotes))
    } catch {
      // ignore
    }
  }, [overlapNotes])

  const getComplaint = (id: string) => complaints.find((c) => c.id === id)

  // Explicit human-in-the-loop actions
  const handleConfirm = (id: string, note?: string) => {
    setOverlapStates((prev) => ({ ...prev, [id]: 'linked' }))
    if (note) {
      setOverlapNotes((prev) => ({ ...prev, [id]: note }))
    }
  }

  const handleReject = (id: string) => {
    setOverlapStates((prev) => ({ ...prev, [id]: 'dismissed' }))
  }

  const handleDefer = (id: string) => {
    setOverlapStates((prev) => ({ ...prev, [id]: 'deferred' }))
  }

  const handleReset = (id: string) => {
    setOverlapStates((prev) => {
      const copy = { ...prev }
      delete copy[id]
      return copy
    })
  }

  const activeList = initialOverlaps.filter((o) => {
    const currentState = overlapStates[o.id]
    if (tab === 'open') return !currentState
    return currentState === tab
  })

  const openCount = initialOverlaps.filter((o) => !overlapStates[o.id]).length
  const linkedCount = initialOverlaps.filter((o) => overlapStates[o.id] === 'linked').length
  const dismissedCount = initialOverlaps.filter((o) => overlapStates[o.id] === 'dismissed').length
  const deferredCount = initialOverlaps.filter((o) => overlapStates[o.id] === 'deferred').length

  return (
    <div className="space-y-6">
      <PageTitle
        title="Cross-Bureau Overlap Detection &amp; Coordination"
        sub="Corroboration matching to surface parallel grievances across Regulation Bureau (RB) and Grievance Cell (PGRC)"
        tag="Cross-Bureau Engine"
      />

      {/* Explanatory Banner & Governance Rule */}
      <Card className="border-l-4 border-l-navy-800 bg-gradient-to-r from-navy-50/40 via-white to-white p-4">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-navy-100 p-2 text-navy-800 mt-0.5">
            <GitMerge size={20} />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-900">
              Cross-Bureau Correlation &amp; Duplicate Safeguard
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed max-w-4xl">
              Institutions frequently face simultaneous inquiries when students file grievances with{' '}
              <strong>PGRC</strong> (e.g. fees, faculty shortages) while parents or whistleblowers
              submit parallel complaints to the <strong>Regulation Bureau (RB)</strong>. This module
              clusters related dockets based on institution ID, category intersection, shared keywords,
              and timeline proximity to surface potential overlaps for officer review.
            </p>
            <div className="mt-2 flex items-center gap-1.5 text-[11px] font-semibold text-amber-900 bg-amber-50 px-2.5 py-1 rounded border border-amber-200">
              <ShieldAlert size={14} className="text-amber-700 flex-shrink-0" />
              <span>
                Mandatory Governance Rule: Officers must explicitly confirm, reject, or defer suggestions. Cases are never automatically merged, closed, or transferred.
              </span>
            </div>
          </div>
        </div>
      </Card>

      {/* Review Status Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setTab('open')}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
            tab === 'open'
              ? 'bg-navy-800 text-white shadow-2xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <span>Pending Review</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'open' ? 'bg-amber-500 text-slate-900 font-bold' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {openCount}
          </span>
        </button>

        <button
          onClick={() => setTab('linked')}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
            tab === 'linked'
              ? 'bg-navy-800 text-white shadow-2xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <span>Confirmed Coordination Links</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'linked' ? 'bg-emerald-500 text-white font-bold' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {linkedCount}
          </span>
        </button>

        <button
          onClick={() => setTab('dismissed')}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
            tab === 'dismissed'
              ? 'bg-navy-800 text-white shadow-2xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <span>Rejected as Independent</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'dismissed' ? 'bg-slate-400 text-white' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {dismissedCount}
          </span>
        </button>

        <button
          onClick={() => setTab('deferred')}
          className={`flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-bold transition ${
            tab === 'deferred'
              ? 'bg-navy-800 text-white shadow-2xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          <span>Deferred for Further Evidence</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'deferred' ? 'bg-amber-400 text-slate-900 font-bold' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {deferredCount}
          </span>
        </button>
      </div>

      {/* Overlaps List */}
      <div className="space-y-5">
        {activeList.map((overlap) => {
          const compA = getComplaint(overlap.a)
          const compB = getComplaint(overlap.b)

          if (!compA || !compB) return null

          const isHigh = overlap.similarity >= 85
          const isModerate = overlap.similarity >= 65 && overlap.similarity < 85

          return (
            <Card
              key={overlap.id}
              className={`border-t-4 ${
                isHigh
                  ? 'border-t-rose-600'
                  : isModerate
                  ? 'border-t-amber-500'
                  : 'border-t-slate-400'
              }`}
            >
              {/* Header with Similarity Score & Human Decision Buttons */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-50 text-navy-800 font-bold">
                    <GitMerge size={16} />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      Cluster #{overlap.id.toUpperCase()} • {instName(compA.institutionId)}
                    </h3>
                    <p className="text-xs text-slate-500">
                      Permanent ID: <strong>{compA.institutionPermanentId || '1-4821039'}</strong> • Comparing {compA.id} ({compA.bureau}) &amp; {compB.id} ({compB.bureau})
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <div
                      className={`text-lg font-bold font-mono ${
                        isHigh
                          ? 'text-rose-600'
                          : isModerate
                          ? 'text-amber-600'
                          : 'text-slate-600'
                      }`}
                    >
                      {overlap.similarity}% Match
                    </div>
                    <div className="text-[10px] font-semibold text-slate-400 uppercase">
                      Corroboration Score
                    </div>
                  </div>

                  {/* Actions depending on state */}
                  {tab === 'open' ? (
                    <div className="flex items-center gap-1.5">
                      <Button
                        variant="teal"
                        size="sm"
                        onClick={() =>
                          handleConfirm(
                            overlap.id,
                            `Confirmed by ${currentUser?.name || 'Officer'} on ${TODAY}`
                          )
                        }
                        className="text-xs"
                      >
                        <Check size={13} />
                        <span>Confirm Link</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleReject(overlap.id)}
                        className="text-xs text-slate-700"
                      >
                        <X size={13} />
                        <span>Reject</span>
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDefer(overlap.id)}
                        className="text-xs text-amber-700 hover:bg-amber-50"
                      >
                        <PauseCircle size={13} />
                        <span>Defer</span>
                      </Button>
                    </div>
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleReset(overlap.id)}
                      className="text-xs text-slate-500"
                    >
                      Reopen Review
                    </Button>
                  )}
                </div>
              </div>

              {/* Status Note Banner for Processed Overlaps */}
              {tab === 'linked' && (
                <div className="mt-3 rounded-lg bg-emerald-50 p-2.5 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 size={15} className="text-emerald-700 flex-shrink-0" />
                    <span>
                      Confirmed Relationship: Cross-bureau information sharing established. Both files remain active independent dockets.
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-800">
                    {overlapNotes[overlap.id] || 'Verified by Bureau'}
                  </span>
                </div>
              )}

              {tab === 'deferred' && (
                <div className="mt-3 rounded-lg bg-amber-50 p-2.5 border border-amber-200 text-xs text-amber-900 flex items-center gap-2">
                  <Clock size={15} className="text-amber-700 flex-shrink-0" />
                  <span>
                    Deferred for Investigation: Awaiting preliminary inquiry responses from college management before deciding coordination link.
                  </span>
                </div>
              )}

              {/* Side-by-side Case Comparison */}
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {/* Case A */}
                <div
                  onClick={() => onOpen(compA.id)}
                  className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 hover:border-slate-300 transition cursor-pointer group"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-navy-800 group-hover:text-teal-700">
                        {compA.id}
                      </span>
                      <Badge v={compA.bureau} />
                      <span className="text-[10px] font-mono text-slate-500">
                        PID: {compA.institutionPermanentId || '1-4821039'}
                      </span>
                    </div>
                    <Badge v={compA.priority} dot />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">
                    {compA.title}
                  </h4>
                  <p className="mt-1 text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {compA.description}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-200/40">
                    <span>Filed: {fmt(compA.date)}</span>
                    <span className="text-navy-700 font-semibold flex items-center gap-1 group-hover:underline">
                      <span>View File</span>
                      <ExternalLink size={11} />
                    </span>
                  </div>
                </div>

                {/* Case B */}
                <div
                  onClick={() => onOpen(compB.id)}
                  className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 hover:border-slate-300 transition cursor-pointer group"
                >
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-navy-800 group-hover:text-teal-700">
                        {compB.id}
                      </span>
                      <Badge v={compB.bureau} />
                      <span className="text-[10px] font-mono text-slate-500">
                        PID: {compB.institutionPermanentId || '1-4821039'}
                      </span>
                    </div>
                    <Badge v={compB.priority} dot />
                  </div>
                  <h4 className="text-xs font-bold text-slate-900 leading-snug line-clamp-1">
                    {compB.title}
                  </h4>
                  <p className="mt-1 text-xs text-slate-600 line-clamp-3 leading-relaxed">
                    {compB.description}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400 pt-2 border-t border-slate-200/40">
                    <span>Filed: {fmt(compB.date)}</span>
                    <span className="text-navy-700 font-semibold flex items-center gap-1 group-hover:underline">
                      <span>View File</span>
                      <ExternalLink size={11} />
                    </span>
                  </div>
                </div>
              </div>

              {/* Similarity Corroboration Reasons */}
              <div className="mt-4 rounded-lg bg-white p-3 border border-slate-200/80">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5 flex items-center gap-1">
                  <Info size={13} className="text-navy-600" />
                  <span>Overlap Corroboration &amp; Matching Points:</span>
                </div>
                <ul className="grid gap-1 sm:grid-cols-2 text-xs text-slate-700">
                  {overlap.reasons.map((r, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-teal-500 flex-shrink-0" />
                      <span>{r}</span>
                    </li>
                  ))}
                </ul>
                {overlap.notes && (
                  <div className="mt-2 text-[11px] text-slate-500 border-t border-slate-100 pt-1.5 italic">
                    Analyst Recommendation: {overlap.notes}
                  </div>
                )}
              </div>
            </Card>
          )
        })}

        {activeList.length === 0 && (
          <Card className="py-16 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-400">
              <CheckCircle2 size={24} className="text-emerald-500" />
            </div>
            <h4 className="mt-3 text-sm font-semibold text-slate-800">
              No Overlaps in &quot;{tab === 'open' ? 'Pending Review' : tab}&quot;
            </h4>
            <p className="mt-1 text-xs text-slate-500">
              All detected complaint overlaps in this category have been processed.
            </p>
          </Card>
        )}
      </div>
    </div>
  )
}
