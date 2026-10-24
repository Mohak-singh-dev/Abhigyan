import { useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ExternalLink,
  GitMerge,
  Info,
  Layers,
  Sparkles,
  X,
} from 'lucide-react'
import type { Complaint } from '../types'
import { fmt, instName, overlaps } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle } from '../components/ui'

interface OverlapsProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
}

export default function Overlaps({ complaints, onOpen }: OverlapsProps) {
  const [overlapStates, setOverlapStates] = useState<Record<string, 'linked' | 'dismissed'>>({
    o2: 'linked',
    o4: 'linked',
    o5: 'dismissed',
  })
  const [tab, setTab] = useState<'open' | 'linked' | 'dismissed'>('open')

  const getComplaint = (id: string) => complaints.find((c) => c.id === id)

  const handleLink = (id: string) => {
    setOverlapStates((prev) => ({ ...prev, [id]: 'linked' }))
  }

  const handleDismiss = (id: string) => {
    setOverlapStates((prev) => ({ ...prev, [id]: 'dismissed' }))
  }

  const handleReset = (id: string) => {
    setOverlapStates((prev) => {
      const copy = { ...prev }
      delete copy[id]
      return copy
    })
  }

  const activeList = overlaps.filter((o) => {
    const currentState = overlapStates[o.id]
    if (tab === 'open') return !currentState
    return currentState === tab
  })

  const openCount = overlaps.filter((o) => !overlapStates[o.id]).length
  const linkedCount = overlaps.filter((o) => overlapStates[o.id] === 'linked').length
  const dismissedCount = overlaps.filter((o) => overlapStates[o.id] === 'dismissed').length

  return (
    <div className="space-y-6">
      <PageTitle
        title="Cross-Bureau Overlap Detection"
        sub="Rule-based cross-reference matching to identify duplicate or related complaints across Regulation Bureau (RB) and Grievance Cell (PGRC)"
        tag="SIH Demo Module"
      />

      {/* Explanatory Banner */}
      <Card className="border-l-4 border-l-indigo-600 bg-gradient-to-r from-indigo-50/40 via-white to-white">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-indigo-100 p-2 text-indigo-700 mt-0.5">
            <Sparkles size={20} />
          </div>
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-slate-900">
              Why Cross-Bureau Overlap Monitoring Matters
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed max-w-4xl">
              Institutions frequently face simultaneous inquiries when students file grievances with{' '}
              <strong>PGRC</strong> (e.g. fees, faculty shortages) while parents or whistleblowers
              submit parallel complaints to the <strong>Regulation Bureau (RB)</strong>. This module
              clusters related dockets based on institution ID, category intersection, shared keywords,
              and timeline proximity to surface potential overlaps for officer review.
              <span className="block mt-1 text-slate-400 italic">All match scores are computed from simulated demo data and do not reflect live AI output.</span>
            </p>
          </div>
        </div>
      </Card>

      {/* Tabs */}
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
              tab === 'open' ? 'bg-amber-400 text-slate-900' : 'bg-slate-100 text-slate-600'
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
          <span>Consolidated / Linked</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'linked' ? 'bg-emerald-400 text-slate-900' : 'bg-slate-100 text-slate-600'
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
          <span>Dismissed as Independent</span>
          <span
            className={`rounded-full px-2 py-0.2 text-[10px] ${
              tab === 'dismissed' ? 'bg-slate-400 text-white' : 'bg-slate-100 text-slate-600'
            }`}
          >
            {dismissedCount}
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
              {/* Header with Similarity Score */}
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2.5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-50 text-navy-800 font-bold">
                    <GitMerge size={16} />
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900">
                      Overlap Cluster #{overlap.id.toUpperCase()} • {instName(compA.institutionId)}
                    </h3>
                    <p className="text-xs text-slate-500">
                      Comparing {compA.id} ({compA.bureau}) &amp; {compB.id} ({compB.bureau})
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
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
                      Match Score
                    </div>
                  </div>

                  {/* Actions depending on state */}
                  {tab === 'open' ? (
                    <div className="flex items-center gap-2">
                      <Button
                        variant="teal"
                        size="sm"
                        onClick={() => handleLink(overlap.id)}
                        className="text-xs"
                      >
                        <Check size={14} />
                        <span>Link &amp; Consolidate</span>
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDismiss(overlap.id)}
                        className="text-xs text-slate-600"
                      >
                        <X size={14} />
                        <span>Separate Files</span>
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

              {/* Side-by-side Case Comparison */}
              <div className="mt-4 grid gap-4 md:grid-cols-2">
                {/* Case A */}
                <div
                  onClick={() => onOpen(compA.id)}
                  className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 transition hover:bg-slate-100/70 cursor-pointer group"
                >
                  <div className="flex items-center justify-between gap-2 border-b border-slate-200/60 pb-2 mb-2">
                    <div className="flex items-center gap-2">
                      <Badge v={compA.bureau} />
                      <span className="font-mono text-xs font-bold text-navy-800 group-hover:underline">
                        {compA.id}
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
                  className="rounded-xl border border-slate-200 bg-slate-50/60 p-4 transition hover:bg-slate-100/70 cursor-pointer group"
                >
                  <div className="flex items-center justify-between gap-2 border-b border-slate-200/60 pb-2 mb-2">
                    <div className="flex items-center gap-2">
                      <Badge v={compB.bureau} />
                      <span className="font-mono text-xs font-bold text-navy-800 group-hover:underline">
                        {compB.id}
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

              {/* Similarity Evidence Reasons */}
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
