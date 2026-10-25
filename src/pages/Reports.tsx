import { useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  BarChart3,
  CheckCircle2,
  Download,
  FileSpreadsheet,
  FileText,
  Filter,
  PieChart as PieIcon,
  Printer,
  TrendingUp,
} from 'lucide-react'
import type { Complaint } from '../types'
import { BUREAUS, BUREAU_INFO, STATUSES, TODAY, instName } from '../data'
import { Badge, Button, Card, CardHeader, PageTitle } from '../components/ui'

const PALETTE = ['#0b2250', '#1d4a94', '#0d9488', '#f59e0b', '#dc2626', '#8b5cf6', '#64748b']
const STATUS_COLORS: Record<string, string> = {
  Pending: '#f59e0b',
  'In Progress': '#3b82f6',
  Escalated: '#ef4444',
  Resolved: '#10b981',
}

export default function Reports({ complaints }: { complaints: Complaint[] }) {
  const [reportPeriod, setReportPeriod] = useState('Current Academic Year (2026-27)')
  const [downloadSuccess, setDownloadSuccess] = useState(false)

  // 1. Complaint Categories data
  const categoryCounts: Record<string, number> = {}
  complaints.forEach((c) => {
    categoryCounts[c.category] = (categoryCounts[c.category] || 0) + 1
  })
  const categoryData = Object.entries(categoryCounts).map(([name, value]) => ({ name, value }))

  // 2. Status Distribution data
  const statusData = STATUSES.map((s) => ({
    name: s,
    value: complaints.filter((c) => c.status === s).length,
  }))

  // 3. Bureau-wise stacked bar data
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

  // 4. Monthly Trend Data (Simulated 6-Month Intake vs Closure)
  const monthlyData = [
    { month: 'May 2026', Filed: 12, Resolved: 10 },
    { month: 'Jun 2026', Filed: 18, Resolved: 14 },
    { month: 'Jul 2026', Filed: 24, Resolved: 19 },
    { month: 'Aug 2026', Filed: 22, Resolved: 21 },
    { month: 'Sep 2026', Filed: 28, Resolved: 25 },
    { month: 'Oct 2026', Filed: 15, Resolved: 11 },
  ]

  const handlePrint = () => {
    window.print()
  }

  const handleDownloadDossierCSV = () => {
    const headers = [
      'Case ID',
      'AICTE Permanent ID',
      'Institution Name',
      'Bureau / Cell',
      'Category',
      'Priority',
      'Investigating Officer',
      'Status',
      'Filing Date',
      'Statutory SLA Due Date',
      'Subject Title',
      'Case Description',
    ]

    const escapeCsv = (str: string) => {
      const escaped = (str || '').replace(/"/g, '""')
      return `"${escaped}"`
    }

    const rows = complaints.map((c) => [
      c.id,
      c.institutionPermanentId || '',
      instName(c.institutionId),
      c.bureau,
      c.category,
      c.priority,
      c.officer,
      c.status,
      c.date,
      c.due,
      c.title,
      c.description.replace(/[\r\n]+/g, ' '),
    ])

    const csvContent = [
      headers.map(escapeCsv).join(','),
      ...rows.map((row) => row.map(escapeCsv).join(',')),
    ].join('\r\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `AICTE_Abhigyan_Compliance_Dossier_${TODAY}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    setDownloadSuccess(true)
    setTimeout(() => {
      setDownloadSuccess(false)
    }, 6000)
  }

  return (
    <div className="space-y-6">
      <PageTitle
        title="Reports, Trends &amp; Data Analytics"
        sub="Statutory compliance metrics, resolution throughput, and cross-bureau intelligence"
        action={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handlePrint} className="text-xs">
              <Printer size={14} />
              <span>Print Dossier (PDF)</span>
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleDownloadDossierCSV}
              className="text-xs"
            >
              <Download size={14} />
              <span>Download Dossier (CSV)</span>
            </Button>
          </div>
        }
      />

      {downloadSuccess && (
        <div className="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-xs text-emerald-900 shadow-2xs">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 size={16} className="text-emerald-700 shrink-0" />
            <span>
              Real case data dossier successfully generated and downloaded as <strong>AICTE_Abhigyan_Compliance_Dossier_{TODAY}.csv</strong> ({complaints.length} records). For printable PDF output, use the &quot;Print Dossier (PDF)&quot; feature.
            </span>
          </div>
          <button
            onClick={() => setDownloadSuccess(false)}
            className="text-emerald-700 hover:text-emerald-950 font-semibold text-xs ml-4"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Summary KPI Ribbon */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-navy-50 p-3 text-navy-800">
            <FileText size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{complaints.length}</div>
            <div className="text-xs text-slate-500">Cumulative Registered Cases</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-emerald-50 p-3 text-emerald-700">
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">
              {Math.round(
                (complaints.filter((c) => c.status === 'Resolved').length / complaints.length) * 100
              )}
              %
            </div>
            <div className="text-xs text-slate-500">Resolution Clearance Rate</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-blue-50 p-3 text-blue-700">
            <TrendingUp size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">11.4 Days</div>
            <div className="text-xs text-slate-500">Avg. Redressal Turnaround (simulated)</div>
          </div>
        </Card>

        <Card className="flex items-center gap-3">
          <div className="rounded-xl bg-indigo-50 p-3 text-indigo-700">
            <BarChart3 size={22} />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">92%</div>
            <div className="text-xs text-slate-500">Overlap Redundancy Prevented (simulated)</div>
          </div>
        </Card>
      </div>

      {/* Charts Grid Row 1 */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Category Breakdown */}
        <Card>
          <CardHeader
            title="Grievance Subject Matter Classification"
            sub="Distribution of complaints across key regulatory focus areas"
          />
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  dataKey="value"
                  nameKey="name"
                  outerRadius={95}
                  innerRadius={45}
                  paddingAngle={3}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  labelLine={false}
                >
                  {categoryData.map((_, i) => (
                    <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
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
        </Card>

        {/* Resolution Status Distribution */}
        <Card>
          <CardHeader
            title="Resolution Status Distribution"
            sub="Active case progression and completion stage"
          />
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={statusData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius={60}
                  outerRadius={95}
                  paddingAngle={4}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {statusData.map((s) => (
                    <Cell key={s.name} fill={STATUS_COLORS[s.name] || '#64748b'} />
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
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Charts Grid Row 2: Monthly Trends and Bureau Breakdown */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Bureau-wise Stacked Bar Chart */}
        <Card className="lg:col-span-2">
          <CardHeader
            title="Bureau-Wise Workload &amp; Resolution Status"
            sub="Comparative volume and disposal efficiency across AICTE Bureaus"
          />
          <div className="h-80 w-full pt-2">
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
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                {STATUSES.map((s) => (
                  <Bar
                    key={s}
                    dataKey={s}
                    stackId="a"
                    fill={STATUS_COLORS[s]}
                    radius={s === 'Escalated' ? [4, 4, 0, 0] : [0, 0, 0, 0]}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* 6-Month Intake vs Resolution Trend */}
        <Card>
          <CardHeader
            title="6-Month Intake vs Closure Trend"
            sub="Simulated illustrative data — not sourced from live AICTE records"
          />
          <div className="h-80 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="month" fontSize={10} stroke="#64748b" tickLine={false} />
                <YAxis fontSize={12} stroke="#64748b" tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    borderRadius: '8px',
                    borderColor: '#e2e8f0',
                    fontSize: '12px',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Line
                  type="monotone"
                  dataKey="Filed"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
                <Line
                  type="monotone"
                  dataKey="Resolved"
                  stroke="#10b981"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  )
}
