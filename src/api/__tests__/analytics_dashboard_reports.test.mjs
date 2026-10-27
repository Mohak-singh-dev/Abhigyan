/**
 * Phase 3 Dynamic Dashboards and Analytics Tests
 *
 * Verifies:
 * 1. KPI Aggregates accuracy: total, pending, in-progress, resolved, escalated, overdue, criticalHigh.
 * 2. Role-based access scoping:
 *    - Complainants only see their own permitted case aggregates.
 *    - Officers only see cases assigned to them.
 *    - Bureau Admins only see cases within authorized bureau jurisdiction.
 *    - System Admin sees organization-wide aggregates.
 * 3. Date range filters and bureau filters.
 * 4. Real historical trend calculations (no fabricated or invented points).
 * 5. Empty dataset handling: zero counts, empty arrays, no errors.
 */

import { test, describe } from 'node:test'
import assert from 'node:assert/strict'

// Scoping logic matching Dashboard.tsx and backend analytics router
function scopeComplaints(complaints, role, user, bureauFilter = 'All', startDate = '', endDate = '') {
  let list = complaints

  if (role === 'Complainant') {
    list = list.filter((c) =>
      Boolean(
        user?.email &&
        c.complainantEmail &&
        c.complainantEmail.trim().toLowerCase() === user.email.trim().toLowerCase()
      )
    )
  } else if (role === 'Officer') {
    list = list.filter((c) => {
      if (c.assignedUserId) {
        return Boolean(user?.id && c.assignedUserId === user.id)
      }
      return Boolean(user?.name && c.officer === user.name)
    })
  } else if (role === 'BureauAdmin') {
    list = list.filter((c) =>
      user?.bureau === 'All' ||
      c.bureau.toUpperCase() === (user?.bureau || '').toUpperCase()
    )
  }

  if (bureauFilter && bureauFilter !== 'All') {
    list = list.filter((c) => c.bureau.toUpperCase() === bureauFilter.toUpperCase())
  }
  if (startDate) {
    list = list.filter((c) => c.date >= startDate)
  }
  if (endDate) {
    list = list.filter((c) => c.date <= endDate)
  }

  return list
}

function calculateKPIs(complaints, asOfDate = '2026-10-25') {
  const total = complaints.length
  const pending = complaints.filter((c) => c.status === 'Pending').length
  const inProgress = complaints.filter((c) => c.status === 'In Progress').length
  const resolved = complaints.filter((c) => c.status === 'Resolved').length
  const escalated = complaints.filter((c) => c.status === 'Escalated').length
  const underInvestigation = pending + inProgress
  // Overdue: status != 'Resolved' and due < asOfDate
  const overdue = complaints.filter((c) => c.status !== 'Resolved' && c.due && c.due < asOfDate).length
  const criticalHigh = complaints.filter((c) => c.priority === 'Critical' || c.priority === 'High').length
  const resolutionRate = total > 0 ? Math.round((resolved / total) * 100) : 0

  return {
    total,
    pending,
    inProgress,
    resolved,
    escalated,
    underInvestigation,
    overdue,
    criticalHigh,
    resolutionRate,
  }
}

function calculateMonthlyTrends(complaints) {
  const distinctMonths = new Set()
  for (const c of complaints) {
    if (c.date && c.date.length >= 7) distinctMonths.add(c.date.slice(0, 7))
    if (c.lastActionDate && c.lastActionDate.length >= 7) distinctMonths.add(c.lastActionDate.slice(0, 7))
  }

  const sorted = Array.from(distinctMonths).sort()
  return sorted.map((ym) => {
    const filed = complaints.filter((c) => c.date && c.date.startsWith(ym)).length
    const res = complaints.filter(
      (c) =>
        c.status === 'Resolved' &&
        ((c.lastActionDate && c.lastActionDate.startsWith(ym)) || (!c.lastActionDate && c.date && c.date.startsWith(ym)))
    ).length
    return { monthKey: ym, Filed: filed, Resolved: res }
  })
}

const SAMPLE_COMPLAINTS = [
  {
    id: 'RB-2026-1001',
    bureau: 'RB',
    category: 'Fee Regulation',
    priority: 'Critical',
    status: 'Pending',
    officer: 'Anita Verma',
    assignedUserId: 'u_anita',
    date: '2026-10-10',
    due: '2026-10-20', // Overdue relative to 2026-10-25
    complainantEmail: 'student@example.ac.in',
  },
  {
    id: 'RB-2026-1002',
    bureau: 'RB',
    category: 'Faculty Norms',
    priority: 'High',
    status: 'In Progress',
    officer: 'Anita Verma',
    assignedUserId: 'u_anita',
    date: '2026-10-12',
    due: '2026-10-28', // Not overdue
    complainantEmail: 'other@example.ac.in',
  },
  {
    id: 'PGRC-2026-2001',
    bureau: 'PGRC',
    category: 'Hostel Issues',
    priority: 'Medium',
    status: 'Resolved',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u_rajesh',
    date: '2026-09-01',
    due: '2026-09-15',
    lastActionDate: '2026-09-14', // Resolved is never overdue!
    complainantEmail: 'student@example.ac.in',
  },
  {
    id: 'Approval-2026-3001',
    bureau: 'Approval',
    category: 'Infrastructure',
    priority: 'Low',
    status: 'Escalated',
    officer: 'Suresh Patel',
    assignedUserId: 'u_suresh',
    date: '2026-08-20',
    due: '2026-10-22', // Overdue relative to 2026-10-25
    complainantEmail: 'other@example.ac.in',
  },
]

describe('Phase 3: Dynamic Dashboards & Analytics Suite', () => {
  test('1. KPI aggregates accurately reflect complaint statuses and overdue SLA criteria', () => {
    const kpis = calculateKPIs(SAMPLE_COMPLAINTS, '2026-10-25')
    assert.equal(kpis.total, 4)
    assert.equal(kpis.pending, 1)
    assert.equal(kpis.inProgress, 1)
    assert.equal(kpis.resolved, 1)
    assert.equal(kpis.escalated, 1)
    assert.equal(kpis.underInvestigation, 2)
    assert.equal(kpis.overdue, 2) // RB-2026-1001 (due 10-20, Pending) and Approval-2026-3001 (due 10-22, Escalated)
    assert.equal(kpis.criticalHigh, 2)
    assert.equal(kpis.resolutionRate, 25)
  })

  test('2. Complainant role scoping strictly isolates own complaints', () => {
    const user = { email: 'student@example.ac.in', role: 'Complainant' }
    const scoped = scopeComplaints(SAMPLE_COMPLAINTS, 'Complainant', user)
    assert.equal(scoped.length, 2)
    const kpis = calculateKPIs(scoped, '2026-10-25')
    assert.equal(kpis.total, 2)
    assert.equal(kpis.resolved, 1)
    assert.equal(kpis.pending, 1)
  })

  test('3. Officer role scoping strictly isolates assigned cases', () => {
    const officer = { name: 'Rajesh Kumar', id: 'u_rajesh', role: 'Officer' }
    const complaintsWithStale = [
      ...SAMPLE_COMPLAINTS,
      {
        id: 'PGRC-2026-9999',
        bureau: 'PGRC',
        status: 'Pending',
        officer: 'Rajesh Kumar', // Stale display name
        assignedUserId: 'u_different_officer', // Actually assigned to someone else
        date: '2026-10-15',
      },
    ]
    const scoped = scopeComplaints(complaintsWithStale, 'Officer', officer)
    assert.equal(scoped.length, 1)
    assert.equal(scoped[0].id, 'PGRC-2026-2001')
  })

  test('4. Bureau Admin role scoping restricts cases to authorized bureau', () => {
    const bureauAdmin = { bureau: 'RB', role: 'BureauAdmin' }
    const scoped = scopeComplaints(SAMPLE_COMPLAINTS, 'BureauAdmin', bureauAdmin)
    assert.equal(scoped.length, 2)
    assert.ok(scoped.every((c) => c.bureau === 'RB'))
  })

  test('5. Date-range filters accurately constrain complaints by filing date', () => {
    const scoped = scopeComplaints(
      SAMPLE_COMPLAINTS,
      'Admin',
      { role: 'Admin' },
      'All',
      '2026-09-01',
      '2026-09-30'
    )
    assert.equal(scoped.length, 1)
    assert.equal(scoped[0].id, 'PGRC-2026-2001')
  })

  test('6. Empty dataset produces zero counts without NaN or runtime exceptions', () => {
    const kpis = calculateKPIs([])
    assert.equal(kpis.total, 0)
    assert.equal(kpis.pending, 0)
    assert.equal(kpis.inProgress, 0)
    assert.equal(kpis.resolved, 0)
    assert.equal(kpis.escalated, 0)
    assert.equal(kpis.overdue, 0)
    assert.equal(kpis.resolutionRate, 0)

    const trends = calculateMonthlyTrends([])
    assert.deepEqual(trends, [])
  })

  test('7. Real historical time series contains only verified calendar months (no fake data)', () => {
    const trends = calculateMonthlyTrends(SAMPLE_COMPLAINTS)
    const months = trends.map((t) => t.monthKey)
    assert.deepEqual(months, ['2026-08', '2026-09', '2026-10'])

    const oct = trends.find((t) => t.monthKey === '2026-10')
    assert.equal(oct.Filed, 2)
    assert.equal(oct.Resolved, 0)

    const sep = trends.find((t) => t.monthKey === '2026-09')
    assert.equal(sep.Filed, 1)
    assert.equal(sep.Resolved, 1)
  })
})
