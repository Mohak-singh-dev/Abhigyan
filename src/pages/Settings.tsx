import { useState } from 'react'
import {
  Bell,
  CheckCircle2,
  Database,
  Globe,
  Lock,
  Save,
  Shield,
  Sliders,
  Sparkles,
  Users,
} from 'lucide-react'
import { Badge, Button, Card, CardHeader, PageTitle } from '../components/ui'

export default function Settings() {
  const [similarityThreshold, setSimilarityThreshold] = useState(75)
  const [slaCritical, setSlaCritical] = useState(3)
  const [slaHigh, setSlaHigh] = useState(7)
  const [slaMedium, setSlaMedium] = useState(14)
  const [autoEscalate, setAutoEscalate] = useState(true)
  const [emailAlerts, setEmailAlerts] = useState(true)
  const [savedBanner, setSavedBanner] = useState(false)

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault()
    setSavedBanner(true)
    setTimeout(() => setSavedBanner(false), 4000)
  }

  return (
    <div className="space-y-6 max-w-5xl">
      <PageTitle
        title="System &amp; Bureau Settings"
        sub="Configure cross-bureau overlap detection thresholds, statutory SLA rules, and alert mechanisms"
      />

      {savedBanner && (
        <div className="flex items-center gap-2 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-xs font-semibold text-emerald-800 shadow-2xs animate-in fade-in">
          <CheckCircle2 size={16} className="text-emerald-600" />
          <span>Configuration successfully updated in local AICTE CaseTrack environment!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Overlap Engine Configuration */}
        <Card>
          <CardHeader
            title="AI Cross-Bureau Overlap Detection Engine"
            sub="Set sensitivity parameters for flagging parallel complaints between RB and PGRC"
            action={<Badge v="Core Engine" />}
          />

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between text-xs font-semibold text-slate-800">
                <span>Minimum Similarity Threshold to Flag Overlap:</span>
                <span className="font-mono text-sm text-navy-800 bg-navy-50 px-2 py-0.5 rounded border border-navy-100">
                  {similarityThreshold}%
                </span>
              </div>
              <input
                type="range"
                min="50"
                max="95"
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
                className="w-full accent-navy-800 mt-2"
              />
              <div className="flex justify-between text-[11px] text-slate-400 mt-1">
                <span>50% (Permissive / Higher recall)</span>
                <span>75% (Recommended for SIH)</span>
                <span>95% (Strict / High precision)</span>
              </div>
            </div>

            <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600 border border-slate-100 leading-relaxed">
              When two complaints against the same institution match above{' '}
              <strong>{similarityThreshold}%</strong> based on TF-IDF semantic embeddings and keyword
              matching, CaseTrack flags an urgent alert in both the <strong>Regulation Bureau (RB)</strong>{' '}
              and <strong>Public Grievance Redressal Cell (PGRC)</strong> dockets.
            </div>
          </div>
        </Card>

        {/* SLA Window Configuration */}
        <Card>
          <CardHeader
            title="Statutory Redressal SLA Windows (Business Days)"
            sub="Prescribed timeframes under the AICTE Grievance Redressal Regulations"
          />

          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Critical Severity SLA (Days)
              </label>
              <input
                type="number"
                min="1"
                max="10"
                value={slaCritical}
                onChange={(e) => setSlaCritical(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-bold text-slate-800 focus:border-navy-600 focus:outline-none"
              />
              <p className="mt-1 text-[10px] text-slate-400">Hostel hazard, ragging, unapproved courses</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                High Priority SLA (Days)
              </label>
              <input
                type="number"
                min="3"
                max="20"
                value={slaHigh}
                onChange={(e) => setSlaHigh(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-bold text-slate-800 focus:border-navy-600 focus:outline-none"
              />
              <p className="mt-1 text-[10px] text-slate-400">Excess fee collections, admission bypass</p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Standard / Medium SLA (Days)
              </label>
              <input
                type="number"
                min="5"
                max="45"
                value={slaMedium}
                onChange={(e) => setSlaMedium(Number(e.target.value))}
                className="w-full rounded-lg border border-slate-300 p-2 text-xs font-bold text-slate-800 focus:border-navy-600 focus:outline-none"
              />
              <p className="mt-1 text-[10px] text-slate-400">Equipment deficiency, syllabus dispute</p>
            </div>
          </div>
        </Card>

        {/* Automation & Escalation Rules */}
        <Card>
          <CardHeader
            title="Automated Surveillance &amp; Bureau Notification Rules"
            sub="Automatic escalation triggers upon statutory deadline breach"
          />

          <div className="space-y-4 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <div>
                <h4 className="font-bold text-slate-900">Automatic Bureau Head Escalation</h4>
                <p className="text-slate-500 mt-0.5">
                  Escalate any case exceeding statutory SLA directly to Bureau Chief &amp; Member Secretary.
                </p>
              </div>
              <input
                type="checkbox"
                checked={autoEscalate}
                onChange={(e) => setAutoEscalate(e.target.checked)}
                className="h-4 w-4 rounded accent-navy-800"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100">
              <div>
                <h4 className="font-bold text-slate-900">Daily Digest Email Notifications</h4>
                <p className="text-slate-500 mt-0.5">
                  Send morning summary of pending files and overlap alerts to designated investigating officers.
                </p>
              </div>
              <input
                type="checkbox"
                checked={emailAlerts}
                onChange={(e) => setEmailAlerts(e.target.checked)}
                className="h-4 w-4 rounded accent-navy-800"
              />
            </div>
          </div>
        </Card>

        {/* Save button */}
        <div className="flex justify-end gap-3 pt-2">
          <Button type="submit" variant="primary" size="md">
            <Save size={15} />
            <span>Save Configuration Preferences</span>
          </Button>
        </div>
      </form>
    </div>
  )
}
