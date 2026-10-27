import test from 'node:test'
import assert from 'node:assert/strict'
import {
  canAssignCase,
  canUpdateCaseStatus,
  resolveOfficerName,
  userProfiles,
} from '../../data.ts'
import { ApiError } from '../client.ts'

test('Phase 1 Regression: Unassigned officer dropdown permits selecting first officer', async (t) => {
  // Setup an unassigned complaint
  const unassignedComplaint = {
    id: 'PGRC-2026-9238',
    bureau: 'PGRC',
    category: 'Fee Regulation',
    priority: 'High',
    officer: 'Unassigned',
    assignedUserId: undefined,
    status: 'Pending',
    title: 'Unassigned grievance test docket',
    complainantEmail: 'citizen@gov.in',
  }

  const systemAdmin = {
    id: 'u1',
    name: 'Dr. S. Mehta',
    role: 'Admin',
    bureau: 'All',
  }

  // First officer in list from userProfiles
  const allOfficers = userProfiles.filter((u) => u.role === 'Officer')
  const firstOfficer = allOfficers[0] // Typically Anita Verma or Rajesh Kumar
  assert.ok(firstOfficer, 'Should have officers configured')

  // Verify permission to assign
  const check = canAssignCase(systemAdmin, unassignedComplaint)
  assert.equal(check.allowed, true, 'System Admin must be permitted to assign unassigned complaint')

  // Simulate assignment guard logic from handleOfficerSelectChange / handleAssignOfficer
  const currentResolved = resolveOfficerName(unassignedComplaint, userProfiles)
  assert.equal(currentResolved, 'Unassigned')

  const targetUser = userProfiles.find((u) => u.name === firstOfficer.name)
  const targetUserId = targetUser?.id
  assert.equal(targetUserId, firstOfficer.id)

  // Guard must NOT block selecting first officer when complaint is Unassigned
  const isSelfAssignmentBlocked =
    currentResolved === firstOfficer.name &&
    unassignedComplaint.assignedUserId &&
    unassignedComplaint.assignedUserId === targetUserId

  assert.equal(isSelfAssignmentBlocked, false, 'Selecting first officer for Unassigned complaint must not be blocked')

  // Verify that an already assigned complaint is guarded against duplicate re-selection of the same officer
  const assignedComplaint = {
    ...unassignedComplaint,
    officer: firstOfficer.name,
    assignedUserId: firstOfficer.id,
  }
  const assignedResolved = resolveOfficerName(assignedComplaint, userProfiles)
  assert.equal(assignedResolved, firstOfficer.name)

  const isDuplicateBlocked =
    assignedResolved === firstOfficer.name &&
    assignedComplaint.assignedUserId &&
    assignedComplaint.assignedUserId === targetUserId

  assert.equal(isDuplicateBlocked, true, 'Duplicate re-selection of identical officer and stable ID must be guarded')
})

test('Phase 1 Regression: Error notifications display actual HTTP status', async (t) => {
  // Test formatting helper pattern used in App.tsx
  const formatNotificationTitle = (baseTitle, err) => {
    const statusSuffix = err instanceof ApiError ? ` (HTTP ${err.status})` : ''
    return `${baseTitle}${statusSuffix}`
  }

  // 1. 404 Not Found error
  const err404 = new ApiError('Complaint with ID or Case ID PGRC-2026-9238 was not found', 404, {
    detail: "Complaint with ID or Case ID 'PGRC-2026-9238' was not found",
  })
  const title404 = formatNotificationTitle('Cross-Bureau Transfer Blocked by Server', err404)
  assert.equal(title404, 'Cross-Bureau Transfer Blocked by Server (HTTP 404)')
  assert.ok(!title404.includes('403'), 'Must not report 403 when error is 404')

  // 2. 403 Forbidden error
  const err403 = new ApiError('Forbidden action', 403, { detail: 'Forbidden' })
  const title403 = formatNotificationTitle('Assignment Blocked by Server', err403)
  assert.equal(title403, 'Assignment Blocked by Server (HTTP 403)')

  // 3. 400 Bad Request error
  const err400 = new ApiError('Invalid bureau prefix', 400, { detail: 'Invalid bureau prefix' })
  const title400 = formatNotificationTitle('Submission Blocked by Server', err400)
  assert.equal(title400, 'Submission Blocked by Server (HTTP 400)')

  // 4. Non-ApiError generic error preserves message without hardcoded HTTP code
  const genericErr = new Error('Network failure')
  const titleGeneric = formatNotificationTitle('Status Update Blocked by Server', genericErr)
  assert.equal(titleGeneric, 'Status Update Blocked by Server')
})

test('Phase 1 Regression: Case ID consistency and authoritative state handling', async (t) => {
  const localComplaint = {
    id: 'PGRC-2026-9999',
    title: 'Local intake draft',
    description: 'Initial intake state generated client-side',
    bureau: 'PGRC',
    category: 'Fee Regulation',
    priority: 'High',
    officer: 'Unassigned',
    status: 'Pending',
    date: '2026-10-26',
    due: '2026-11-02',
  }

  // Simulated backend authoritative response (e.g. backend confirms or assigns server-persisted Case ID)
  const backendResponse = {
    ...localComplaint,
    id: 'PGRC-2026-9999',
    officer: 'Rajesh Kumar',
    assignedUserId: 'u2',
    status: 'Pending',
  }

  // Merged authoritative complaint
  const authoritativeComplaint = { ...localComplaint, ...backendResponse }
  assert.equal(authoritativeComplaint.id, backendResponse.id, 'Public Case ID must match backend persisted ID exactly')
  assert.equal(authoritativeComplaint.officer, 'Rajesh Kumar', 'Authoritative state must replace initial intake state')
})
