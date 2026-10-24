import { useState } from 'react'
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Building2,
  CheckCircle2,
  Clock,
  ExternalLink,
  FilePlus,
  FileText,
  Flame,
  GitMerge,
  HelpCircle,
  Landmark,
  Layers,
  RefreshCw,
  Shield,
  TrendingUp,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Complaint, Page, Role, Status } from '../types'
import { BUREAUS, BUREAU_INFO, CURRENT_OFFICER, TODAY, isOverdue, overlaps } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle, Stat } from '../components/ui'
import ComplaintTable from '../components/ComplaintTable'

interface DashboardProps {
  complaints: Complaint[]
  onOpen: (id: string) => void
  onStatus: (id: string, s: Status) => void
  onNavigate: (page: Page) => void
  currentRole: Role
}

export default function Dashboard({
  complaints,
  onOpen,
  onStatus,
  onNavigate,
  currentRole,
}: DashboardProps) {
  const [bureauFilter, setBureauFilter] = useState<string>('All')

  // Calculated statistics
  const totalCases = complaints.length
  const pendingCases = complaints.filter((c) => c.status === 'Pending').length
  const inProgressCases = complaints.filter((c) => c.status === 'In Progress').length
  const resolvedCases = complaints.filter((c) => c.status === 'Resolved').length
  const escalatedCases = complaints.filter((c) => c.status === 'Escalated').length
  const overdueCases = complaints.filter(isOverdue).length
  const criticalHighCases = complaints.filter(
    (c) => c.priority === 'Critical' || c.priority === 'High'
  ).length
  const pendingOverlaps = overlaps.filter((o) => o.similarity >= 80).length
  const resolutionRate = Math.round((resolvedCases / totalCases) * 100) || 0

  // Filtered recent cases
  const recentCases = complaints
    .filter((c) => bureauFilter === 'All' || c.bureau === bureauFilter)
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, 5)

  // Chart Data: Bureaus
  const bureauData = BUREAUS.map((b) => {
    const list = complaints.filter((c) => c.bureau === b)
    return {
      name: b,
      Resolved: list.filter((c) => c.status === 'Resolved').length,
      'In Progress': list.filter((c) => c.status === 'In Progress').length,
      Pending: list.filter((c) => c.status === 'Pending').length,
      Escalated: list.filter((c) => c.status === 'Escalated').length,
      Total: list.length,
    }
  })

  // Priority Distribution Chart Data
  const priorityData = [
    { name: 'Critical', value: complaints.filter((c) => c.priority === 'Critical').length, color: '#dc2626' },
    { name: 'High', value: complaints.filter((c) => c.priority === 'High').length, color: '#ea580c' },
    { name: 'Medium', value: complaints.filter((c) => c.priority === 'Medium').length, color: '#d97706' },
    { name: 'Low', value: complaints.filter((c) => c.priority === 'Low').length, color: '#64748b' },
  ]

  return (
    <div className="space-y-6">
      {/* Top Banner Alert if any Overdue or Overlaps exist */}
      {overdueCases > 0 && (
        <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-200 bg-red-50/90 p-4 text-red-900 shadow-2xs">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-red-100 p-2 text-red-700">
              <AlertTriangle size={20} />
            </div>
            <div>
              <h4 className="text-sm font-bold">
                {overdueCases} Case{overdueCases > 1 ? 's' : ''} Exceeded Statutory SLA Threshold
              </h4>
              <p className="text-xs text-red-700 mt-0.5">
                Immediate review requested for RB and PGRC grievance files overdue past 14 days.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="danger"
              size="sm"
              onClick={() => onNavigate('tracking')}
              className="text-xs"
            >
              Examine SLA Tracker
            </Button>
          </div>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Stat
          label="Total Complaints"
          value={totalCases}
          icon={FileText}
          color="bg-navy-50 text-navy-800"
          trend="+12%"
          trendLabel="vs last month"
          onClick={() => onNavigate('complaints')}
        />
        <Stat
          label="Under Investigation"
          value={pendingCases + inProgressCases}
          icon={Clock}
          color="bg-blue-50 text-blue-700"
          trend={`${inProgressCases} active`}
          trendLabel="in progress"
          onClick={() => onNavigate('complaints')}
        />
        <Stat
          label="Overdue / SLA Breached"
          value={overdueCases}
          icon={AlertTriangle}
          color="bg-rose-50 text-rose-700"
          trend="Critical"
          trendLabel="Urgent attention"
          onClick={() => onNavigate('tracking')}
        />
        <Stat
          label="Cross-Bureau Overlaps"
          value={pendingOverlaps}
          icon={GitMerge}
          color="bg-indigo-50 text-indigo-700"
          trend="High Match"
          trendLabel="RB ↔ PGRC pairs"
          onClick={() => onNavigate('overlaps')}
        />
        <Stat
          label="Resolved Cases"
          value={resolvedCases}
          icon={CheckCircle2}
          color="bg-emerald-50 text-emerald-700"
          trend={`${resolutionRate}%`}
          trendLabel="closure rate"
          onClick={() => onNavigate('reports')}
        />
        <Stat
          label="Critical / High Priority"
          value={criticalHighCases}
          icon={Flame}
          color="bg-amber-50 text-amber-700"
          trend={`${Math.round((criticalHighCases / totalCases) * 100)}%`}
          trendLabel="of all cases"
          onClick={() => onNavigate('complaints')}
        />
      </div>

      {/* Main Grid: Charts & Analytics */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Bureau Distribution Bar Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Bureau-Wise Complaint Case Distribution"
            sub="Comparative analysis across RB (Regulation), PGRC (Public Grievance), Approval, and Academic"
            action={
              <Button
                variant="outline"
                size="sm"
                onClick={() => onNavigate('reports')}
                className="text-xs"
              >
                Full Analytics &rarr;
              </Button>
            }
          />
          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bureauData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" fontSize={12} stroke="#64748b" tickLine={false} />
                <YAxis allowDecimals={false} fontSize={12} stroke="#64748b" tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    borderColor: '#e2e8f0',
                    fontSize: '12px',
                    boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Resolved" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]} />
                <Bar dataKey="In Progress" stackId="a" fill="#3b82f6" />
                <Bar dataKey="Pending" stackId="a" fill="#f59e0b" />
                <Bar dataKey="Escalated" stackId="a" fill="#ef4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Priority Breakdown Pie Chart */}
        <Card>
          <CardHeader
            title="Severity Distribution"
            sub="Case priority breakdown across all active files"
          />
          <div className="h-56 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {priorityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    borderColor: '#e2e8f0',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 border-t border-slate-100 pt-3 text-xs">
            {priorityData.map((p) => (
              <div key={p.name} className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: p.color }} />
                <span className="text-slate-600 font-medium">{p.name}:</span>
                <span className="font-bold text-slate-800">{p.value}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Cross-Bureau Overlap Highlight Banner */}
      <Card className="border-l-4 border-l-teal-600 bg-gradient-to-r from-teal-50/40 via-white to-white">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-teal-600 text-white shadow-xs">
                <GitMerge size={14} />
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Cross-Bureau Overlap Detection Engine Active
              </h3>
              <Badge v="SIH Innovation" className="bg-teal-100 text-teal-800 border-teal-200" />
            </div>
            <p className="text-xs text-slate-600 max-w-2xl leading-relaxed">
              Monitoring duplicate grievances filed across{' '}
              <strong className="text-indigo-800">Regulation Bureau (RB)</strong> and{' '}
              <strong className="text-teal-800">Public Grievance Redressal Cell (PGRC)</strong>. 5 potential overlaps
              identified with AI similarity confidence up to 94%.
            </p>
          </div>
          <Button
            variant="teal"
            size="sm"
            onClick={() => onNavigate('overlaps')}
            className="text-xs flex items-center gap-1.5"
          >
            <span>Review Overlaps (5)</span>
            <ArrowRight size={13} />
          </Button>
        </div>
      </Card>

      {/* Recent Complaints Table Section */}
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4 mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900">Recent Complaints &amp; Status</h3>
            <p className="text-xs text-slate-500">
              Latest incoming files across technical institutions and AICTE cells
            </p>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 rounded-lg border border-slate-200 bg-slate-50/60 p-1 text-xs">
              {['All', 'RB', 'PGRC', 'Approval', 'Academic'].map((b) => (
                <button
                  key={b}
                  onClick={() => setBureauFilter(b)}
                  className={`rounded-md px-2.5 py-1 text-xs font-semibold transition ${
                    bureauFilter === b
                      ? 'bg-navy-800 text-white shadow-2xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => onNavigate('complaints')}
              className="text-xs"
            >
              All Complaints &rarr;
            </Button>
          </div>
        </div>

        <ComplaintTable
          rows={recentCases}
          onOpen={onOpen}
          onStatus={onStatus}
          compact={false}
          showActions={true}
        />
      </Card>
    </div>
  )
}
